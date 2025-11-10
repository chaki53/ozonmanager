'use client'
import { useEffect, useState } from 'react'
import { apiFetch } from '@/lib/api'
export default function Settings(){
  const [me,setMe] = useState<any>(null)
  const [email,setEmail] = useState('')
  const [pwd,setPwd] = useState({current:'', new1:'', new2:''})
  const [msg,setMsg] = useState<string| null>(null)
  useEffect(()=>{ (async()=>{ const r = await apiFetch('/auth/me'); if(r.ok){ const u = await r.json(); setMe(u); setEmail(u.email) } })() },[])
  async function saveEmail(e:React.FormEvent){ e.preventDefault(); setMsg(null)
    const password = prompt('Введите текущий пароль для подтверждения e-mail:') || ''
    const r = await apiFetch('/auth/change-email', { method:'POST', body: JSON.stringify({ password, new_email: email }) })
    setMsg(r.ok ? 'E-mail обновлён' : await r.text())
  }
  async function savePwd(e:React.FormEvent){ e.preventDefault(); setMsg(null)
    if(pwd.new1 !== pwd.new2){ setMsg('Пароли не совпадают'); return; }
    const r = await apiFetch('/auth/change-password', { method:'POST', body: JSON.stringify({ current_password: pwd.current, new_password: pwd.new1 }) })
    setMsg(r.ok ? 'Пароль обновлён' : await r.text())
  }
  return (<main style={{minHeight:'100vh', background:'#0b0f14', color:'#e5e7eb', padding:24}}>
    <h1>Настройки аккаунта</h1>{me && <p>Вы вошли как <b>{me.email}</b> · роль: {me.role}</p>}{msg && <div style={{margin:'12px 0', color:'#c7f9cc'}}>{msg}</div>}
    <section style={{display:'grid', gap:16, maxWidth:520}}>
      <form onSubmit={saveEmail} style={{background:'#111827', border:'1px solid #1f2937', borderRadius:16, padding:16}}>
        <h3 style={{marginTop:0}}>Сменить e-mail</h3>
        <input value={email} onChange={e=>setEmail(e.target.value)} style={{width:'100%', padding:'10px 12px', borderRadius:10, border:'1px solid #1f2937', background:'#0f172a', color:'#e5e7eb'}}/>
        <div style={{height:8}}/><button style={{background:'linear-gradient(135deg,#22d3ee,#3b82f6)',color:'#001018',border:0,padding:'10px 14px',borderRadius:10,fontWeight:700,cursor:'pointer'}}>Сохранить</button>
      </form>
      <form onSubmit={savePwd} style={{background:'#111827', border:'1px solid #1f2937', borderRadius:16, padding:16}}>
        <h3 style={{marginTop:0}}>Сменить пароль</h3>
        <input type="password" placeholder="Текущий пароль" value={pwd.current} onChange={e=>setPwd({...pwd, current:e.target.value})} style={{width:'100%', padding:'10px 12px', borderRadius:10, border:'1px solid #1f2937', background:'#0f172a', color:'#e5e7eb', marginBottom:8}}/>
        <input type="password" placeholder="Новый пароль" value={pwd.new1} onChange={e=>setPwd({...pwd, new1:e.target.value})} style={{width:'100%', padding:'10px 12px', borderRadius:10, border:'1px solid #1f2937', background:'#0f172a', color:'#e5e7eb', marginBottom:8}}/>
        <input type="password" placeholder="Повторите новый пароль" value={pwd.new2} onChange={e=>setPwd({...pwd, new2:e.target.value})} style={{width:'100%', padding:'10px 12px', borderRadius:10, border:'1px solid #1f2937', background:'#0f172a', color:'#e5e7eb'}}/>
        <div style={{height:8}}/><button style={{background:'linear-gradient(135deg,#22d3ee,#3b82f6)',color:'#001018',border:0,padding:'10px 14px',borderRadius:10,fontWeight:700,cursor:'pointer'}}>Обновить пароль</button>
      </form>
    </section>
  </main>)
}
