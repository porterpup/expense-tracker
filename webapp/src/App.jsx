import React, { useState, useEffect } from 'react'
import { recognizeImage } from './ocr'
import { addExpense, listExpenses } from './idb'

function App(){
  const [image, setImage] = useState(null)
  const [ocrText, setOcrText] = useState('')
  const [merchant, setMerchant] = useState('')
  const [date, setDate] = useState('')
  const [amount, setAmount] = useState('')
  const [expenses, setExpenses] = useState([])

  useEffect(()=>{ loadExpenses() }, [])

  async function loadExpenses(){
    const es = await listExpenses()
    setExpenses(es.reverse())
  }

  async function onFile(e){
    const file = e.target.files && e.target.files[0]
    if(!file) return
    const url = URL.createObjectURL(file)
    setImage(url)
    setOcrText('Recognizing...')
    try{
      const text = await recognizeImage(file)
      setOcrText(text)
      // simple heuristics
      const lines = text.split('\n').map(l=>l.trim()).filter(Boolean)
      const maybeMerchant = lines.find(l=> !/total|amount|subtotal|tax|invoice/i.test(l))
      if(maybeMerchant) setMerchant(maybeMerchant)
      const amt = text.match(/(?:\$|USD\s*)?([0-9]+(?:[.,][0-9]{2}))/)
      if(amt) setAmount(amt[1])
      const dt = text.match(/(\d{4}-\d{2}-\d{2}|\d{1,2}\/\d{1,2}\/\d{2,4})/)
      if(dt) setDate(dt[1])
    }catch(err){
      setOcrText('OCR failed')
    }
  }

  async function save(){
    const rec = {
      merchant,
      date,
      amount: parseFloat((amount||'0').toString().replace(',','.'))||0,
      currency: 'USD',
      category: null,
      raw_text: ocrText,
      source: 'pwa',
      created_at: new Date().toISOString()
    }
    await addExpense(rec)
    setMerchant('')
    setDate('')
    setAmount('')
    setOcrText('')
    setImage(null)
    loadExpenses()
  }

  async function syncFromServer(){
    const base = prompt('Server base URL for sync (e.g. http://localhost:8000)', import.meta.env.VITE_API_URL || 'http://localhost:8000')
    if(!base) return
    try{
      const url = base.replace(/\/+$|\s+/g, '') + '/api/expenses'
      const resp = await fetch(url)
      if(!resp.ok) throw new Error(await resp.text())
      const json = await resp.json()
      const items = json.expenses || []
      const local = await listExpenses()
      const ids = new Set((local||[]).map(e=>e.id))
      let added = 0
      for(const item of items){
        if(ids.has(item.id)) continue
        const rec = {
          id: item.id,
          merchant: item.merchant || '',
          date: item.date || '',
          amount: parseFloat(item.amount) || 0,
          currency: item.currency || 'USD',
          category: item.category || null,
          raw_text: item.raw_text || '',
          source: 'server',
          created_at: item.created_at || new Date().toISOString()
        }
        await addExpense(rec)
        added++
      }
      await loadExpenses()
      alert(`Imported ${added} new expenses (${items.length} on server)`)
    }catch(err){
      alert('Sync failed: ' + (err.message || err))
    }
  }

  function exportCsv(){
    const header = ['id','merchant','date','amount','currency','category','raw_text','source','created_at']
    const rows = expenses.map(e => header.map(k => '"'+((e[k]||'')+'').replace(/"/g,'""')+'"').join(','))
    const csv = header.join(',') + '\n' + rows.join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'expenses.csv'
    a.click()
  }

  return (
    <div style={{padding:16,maxWidth:720,margin:'0 auto'}}>
      <h1>Expense Tracker (PWA)</h1>
      <input type="file" accept="image/*" onChange={onFile} />
      {image && <img src={image} alt="preview" style={{maxWidth:'100%',marginTop:8}}/>}

      <div style={{marginTop:8}}>
        <label>Merchant<br/>
          <input value={merchant} onChange={e=>setMerchant(e.target.value)} />
        </label>
      </div>
      <div>
        <label>Date<br/>
          <input value={date} onChange={e=>setDate(e.target.value)} />
        </label>
      </div>
      <div>
        <label>Amount<br/>
          <input value={amount} onChange={e=>setAmount(e.target.value)} />
        </label>
      </div>
      <div style={{marginTop:8}}>
        <button onClick={save}>Save</button>
        <button onClick={exportCsv} style={{marginLeft:8}}>Export CSV</button>
        <button onClick={syncFromServer} style={{marginLeft:8}}>Sync from server</button>
      </div>

      <h2>Saved expenses</h2>
      <ul>
        {expenses.map(e=> <li key={e.id}>{e.merchant} — {e.amount} — {e.date} {e.source?`(${e.source})`:''}</li>)}
      </ul>

      <h3>OCR text</h3>
      <pre style={{whiteSpace:'pre-wrap'}}>{ocrText}</pre>
    </div>
  )
}

export default App
