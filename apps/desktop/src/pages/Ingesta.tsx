import { useState } from 'react'

export default function Ingesta(){
  const [resp,setResp] = useState<any>(null)
  async function onUpload(e:any){
    const f = e.target.files[0]
    const form = new FormData()
    form.append('file', f)
    const r = await fetch('http://127.0.0.1:8000/ingesta/procesar',{method:'POST', body:form})
    setResp(await r.json())
  }
  return (
    <div className="p-6">
      <h2>Ingesta</h2>
      <input type="file" onChange={onUpload} />
      <pre>{resp && JSON.stringify(resp,null,2)}</pre>
    </div>
  )
}