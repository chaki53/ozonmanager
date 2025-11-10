'use client'
import { useEffect, useState } from 'react'
import { apiFetch } from '@/lib/api'

type Acc = { id:number; name:string }

export default function SyncPage(){
  const [accs,setAccs] = useState<Acc[]>([])
  const [accountId,setAccountId] = useState<number|''>('')
  const [from,setFrom] = useState('')
  const [to,setTo] = useState('')
  const [msg,setMsg] = useState<string| null>(null)

  useEffect(()=>{ (async()=>{
    const r = await apiFetch('/accounts/'); if(r.ok){ const rows = await r.json(); setAccs(rows) }
  })() },[])

  async function run(e:React.FormEvent){
    e.preventDefault(); setMsg(null)
    const qs = new URLSearchParams()
    if(accountId) qs.set('account_id', String(accountId))
    if(from) qs.set('date_from', from)
    if(to) qs.set('date_to', to)
    const r = await apiFetch(`/sync/run?${qs.toString()}`, { method:'POST' })
    setMsg(r.ok ? await r.text() : await r.text())
  }

  return (
    <main style={{minHeight:'100vh', background:'#0b0f14', color:'#e5e7eb', padding:24}}>
      <h1>Принудительная синхронизация</h1>
      {msg && <pre style={{background:'#0b1220', padding:12, borderRadius:12}}>{msg}</pre>}
      <form onSubmit={run} style={{display:'grid', gap:12, maxWidth:560}}>
        <select value={accountId as any} onChange={e=>setAccountId(e.target.value ? Number(e.target.value) : '')}>
          <option value="">Все активные кабинеты</option>
          {accs.map(a=><option key={a.id} value={a.id}>{a.name}</option>)}
        </select>
        <div style={{display:'flex', gap:8}}>
          <label>с: <input type="date" value={from} onChange={e=>setFrom(e.target.value)}/></label>
          <label>по: <input type="date" value={to} onChange={e=>setTo(e.target.value)}/></label>
        </div>
        <button style={{background:'linear-gradient(135deg,#22d3ee,#3b82f6)',color:'#001018',border:0,padding:'10px 14px',borderRadius:10,fontWeight:700,cursor:'pointer'}}>Синхронизировать</button>
      </form>
    </main>
  )
}
