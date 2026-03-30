import React, { useState, useEffect } from 'react'
import { recognizeImage } from './ocr'
import { addExpense, listExpenses } from './idb'

function App(){
  const [image, setImage] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [ocrText, setOcrText] = useState('')
  const [merchant, setMerchant] = useState('')
  const [date, setDate] = useState('')
  const [amount, setAmount] = useState('')
  const [category, setCategory] = useState('')
  const [expenses, setExpenses] = useState([])
  const [clientAuth, setClientAuth] = useState(() => sessionStorage.getItem('client_auth') || '')
  const [authRequired, setAuthRequired] = useState(false)

  useEffect(()=>{ loadExpenses(); checkAuthRequired() }, [])

  async function checkAuthRequired(){
    try{
      const base = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const resp = await fetch(base.replace(/\/+$/,'') + '/api/auth_required')
      if(resp.ok){
        const j = await resp.json()
        setAuthRequired(!!j.required)
      }
    }catch(e){
      // ignore
    }
  }

  async function loadExpenses(){
    const es = await listExpenses()
    setExpenses(es.reverse())
  }

  async function onFile(e){
    const file = e.target.files && e.target.files[0]
    if(!file) return
    const url = URL.createObjectURL(file)
    setImage(url)
    setImageFile(file)
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
    // generate a client id for local item so local and server can be correlated if desired
    const id = Date.now().toString() + '-' + Math.random().toString(36).slice(2,9)

    // read image as base64 if available
    let receipt_blob = null
    if(imageFile){
      try{
        receipt_blob = await new Promise((resolve, reject)=>{
          const fr = new FileReader()
          fr.onload = ()=>{
            const dataUrl = fr.result
            // strip data:...base64,
            const m = String(dataUrl).match(/base64,(.*)$/)
            resolve(m ? m[1] : null)
          }
          fr.onerror = reject
          fr.readAsDataURL(imageFile)
        })
      }catch(e){
        console.warn('Failed to read image for upload', e)
      }
    }

    const rec = {
      id,
      merchant,
      date,
      amount: parseFloat((amount||'0').toString().replace(',','.'))||0,
      currency: 'USD',
      category: category || null,
      raw_text: ocrText,
      source: 'pwa',
      created_at: new Date().toISOString(),
      receipt_blob
    }
    await addExpense(rec)

    // attempt to push to server (best-effort)
    (async ()=>{
      try{
        const base = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const url = base.replace(/\/+$/,'') + '/api/client_ingest'
        const headers = {
          'Content-Type': 'application/json',
          'X-Client-Id': import.meta.env.VITE_CLIENT_ID || ''
        }
        const auth = sessionStorage.getItem('client_auth') || ''
        if(auth) headers['X-Client-Auth'] = auth
        const res = await fetch(url, {
          method: 'POST',
          headers,
          body: JSON.stringify(rec)
        })
        if(!res.ok){
          console.warn('Sync failed', await res.text())
        }
      }catch(err){
        console.warn('Sync error', err)
      }
    })()

    setMerchant('')
    setDate('')
    setAmount('')
    setCategory('')
    setOcrText('')
    setImage(null)
    setImageFile(null)
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

      {/* Simple auth modal */}
      {authRequired && !clientAuth && (
        <div style={{position:'fixed',left:0,top:0,right:0,bottom:0,background:'rgba(0,0,0,0.5)',display:'flex',alignItems:'center',justifyContent:'center'}}>
          <div style={{background:'#fff',padding:20,borderRadius:8,maxWidth:400,width:'90%'}}>
            <h3>Enter app password</h3>
            <input type="password" placeholder="password" onChange={e=>setClientAuth(e.target.value)} style={{width:'100%'}} />
            <div style={{marginTop:8,textAlign:'right'}}>
              <button onClick={()=>{ sessionStorage.setItem('client_auth', clientAuth); window.location.reload();}}>Submit</button>
            </div>
          </div>
        </div>
      )}

      <input type="file" accept="image/*" capture="environment" onChange={onFile} />
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
      <div>
        <label>Category<br/>
          <select value={category} onChange={e=>setCategory(e.target.value)}>
            <option value="">(None)</option>
            <option value="office">Office</option>
            <option value="meals">Meals</option>
            <option value="travel">Travel</option>
            <option value="supplies">Supplies</option>
            <option value="other">Other</option>
          </select>
        </label>
      </div>
      <div style={{marginTop:8}}>
        <button onClick={save}>Save</button>
        <button onClick={exportCsv} style={{marginLeft:8}}>Export CSV</button>
        <button onClick={syncFromServer} style={{marginLeft:8}}>Sync from server</button>
      </div>

      <h2>Saved expenses</h2>
      <ul>
        {expenses.map(e=> <li key={e.id}>{e.merchant} — {e.amount} — {e.date} {e.category?`[${e.category}]`:''} {e.source?`(${e.source})`:''}</li>)}
      </ul>

      <h3>OCR text</h3>
      <pre style={{whiteSpace:'pre-wrap'}}>{ocrText}</pre>
    </div>
  )
}

export default App
