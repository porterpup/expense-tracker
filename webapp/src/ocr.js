import { createWorker } from 'tesseract.js'

export async function recognizeImage(file){
  const worker = createWorker({
    logger: m => {
      // progress messages
    }
  })
  await worker.load()
  await worker.loadLanguage('eng')
  await worker.initialize('eng')
  const { data: { text } } = await worker.recognize(file)
  await worker.terminate()
  return text
}
