'use client'
import { useState } from 'react'
const API = process.env.NEXT_PUBLIC_API_BASE || ''
export default function LoginPage(){
  const [email, setEmail] = useState('admin@local')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState<string | null>(null)
  async function onSubmit(e: React.FormEvent){
    e.preventDefault(); setError(null)
    try {
      const body = new URLSearchParams({ username: email, password })
      const res = await fetch(`${API}/auth/login`, { method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body, credentials:'include' })
      if(!res.ok){ throw new Error(await res.text() || 'Auth failed') }
      const data = await res.json()
      const token = data?.access_token; if(!token) throw new Error('No token')
      document.cookie = `jwt=${token}; Path=/; SameSite=Lax; Secure`; localStorage.setItem('jwt', token)
      window.location.href = '/dashboard'
    } catch (e:any){ setError(e.message || 'Failed to fetch') }
  }
  return (<main style={{minHeight:'100vh',display:'grid',placeItems:'center',background:'#0b0f14',color:'#e5e7eb'}}>
    <form onSubmit={onSubmit} style={{width:380,background:'#111827',border:'1px solid #1f2937',padding:22,borderRadius:16,boxShadow:'0 10px 30px rgba(0,0,0,.25)'}}>
      <h1 style={{margin:0,fontSize:28,fontWeight:800}}>Вход</h1><p style={{opacity:.7,marginTop:6}}>Почта и пароль</p>
      <div style={{display:'grid',gap:12,marginTop:16}}>
        <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" style={{padding:'10px 12px',borderRadius:10,border:'1px solid #1f2937',background:'#0f172a',color:'#e5e7eb'}}/>
        <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="пароль" style={{padding:'10px 12px',borderRadius:10,border:'1px solid #1f2937',background:'#0f172a',color:'#e5e7eb'}}/>
        {error && <div style={{color:'#fecaca'}}>⚠ {error}</div>}
        <button type="submit" style={{background:'linear-gradient(135deg,#22d3ee,#3b82f6)',color:'#001018',border:0,padding:'10px 14px',borderRadius:10,fontWeight:700,cursor:'pointer'}}>Войти</button>
        <small>API: {API}</small>
      </div>
    </form></main>)
}
