'use client'
import { useEffect, useState } from 'react'
import { apiFetch } from '@/lib/api'

type Acc = { id:number; name:string; is_active:boolean; last_sync_at?:string|null }

export default function AccountsPage(){
  const [rows,setRows] = useState<Acc[]>([])
  const [form,setForm] = useState({name:'', client_id:'', api_key:'', is_active:true})
  const [msg,setMsg] = useState<string| null>(null)

  async function load(){
    const r = await apiFetch('/accounts/'); if(r.ok){ setRows(await r.json()) }
  }
  useEffect(()=>{ load() },[])

  async function add(e:React.FormEvent){
    e.preventDefault(); setMsg(null)
    const r = await apiFetch('/accounts/', { method:'POST', body: JSON.stringify(form) })
    setMsg(r.ok ? 'Кабинет добавлен' : await r.text())
    if(r.ok){ setForm({name:'', client_id:'', api_key:'', is_active:true}); load() }
  }

  async function del(id:number){
    if(!confirm('Удалить кабинет?')) return
    const r = await apiFetch(`/accounts/${id}`, { method:'DELETE' })
    setMsg(r.ok ? 'Удалён' : await r.text()); if(r.ok) load()
  }

  return (
    <main style={{minHeight:'100vh', background:'#0b0f14', color:'#e5e7eb', padding:24}}>
      <h1>Ozon кабинеты</h1>
      {msg && <div style={{margin:'12px 0', color:'#c7f9cc'}}>{msg}</div>}
      <section style={{display:'grid', gridTemplateColumns:'1fr', gap:16, maxWidth:760}}>
        <form onSubmit={add} style={{background:'#111827', border:'1px solid #1f2937', borderRadius:16, padding:16}}>
          <h3 style={{marginTop:0}}>Добавить кабинет</h3>
          <div style={{display:'grid', gap:8}}>
            <input placeholder="Название" value={form.name} onChange={e=>setForm({...form, name:e.target.value})}/>
            <input placeholder="Client-Id" value={form.client_id} onChange={e=>setForm({...form, client_id:e.target.value})}/>
            <input placeholder="Api-Key" value={form.api_key} onChange={e=>setForm({...form, api_key:e.target.value})}/>
            <label style={{opacity:.8}}><input type="checkbox" checked={form.is_active} onChange={e=>setForm({...form, is_active:e.target.checked})}/> Активен</label>
            <button style={{background:'linear-gradient(135deg,#22d3ee,#3b82f6)',color:'#001018',border:0,padding:'10px 14px',borderRadius:10,fontWeight:700,cursor:'pointer'}}>Сохранить</button>
          </div>
        </form>

        <div style={{background:'#111827', border:'1px solid #1f2937', borderRadius:16, padding:16}}>
          <h3 style={{marginTop:0}}>Список</h3>
          <table style={{width:'100%', borderCollapse:'collapse'}}>
            <thead><tr><th>ID</th><th>Название</th><th>Активен</th><th>Last sync</th><th/></tr></thead>
            <tbody>
              {rows.map(r=>(
                <tr key={r.id}>
                  <td>{r.id}</td><td>{r.name}</td><td>{r.is_active?'✓':'—'}</td><td style={{opacity:.7}}>{r.last_sync_at || '—'}</td>
                  <td><button onClick={()=>del(r.id)} style={{background:'transparent', border:'1px solid #334155', color:'#e5e7eb', borderRadius:8, padding:'6px 10px'}}>Удалить</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  )
}
