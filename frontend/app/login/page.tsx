'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function LoginPage(){
  const [email, setEmail] = useState('admin@local')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  async function onSubmit(e: React.FormEvent){
    e.preventDefault()
    setError(null)
    try {
      const res = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: email, password })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data?.detail || 'Auth failed')
      const token = data.access_token || data.token
      if (!token) throw new Error('No token returned')
      // store in cookie for middleware and in localStorage for fetch
      document.cookie = `jwt=${token}; path=/; SameSite=Lax`
      localStorage.setItem('jwt', token)
      router.replace('/dashboard')
    } catch (e:any) {
      setError(e.message)
    }
  }

  return (
    <main style={{minHeight:'100vh', display:'grid', placeItems:'center', background:'#0b0f14', color:'#e5e7eb'}}>
      <form onSubmit={onSubmit} style={{width:360, background:'#111827', border:'1px solid #1f2937', padding:20, borderRadius:16}}>
        <h1 style={{margin:0, fontSize:24, fontWeight:800}}>Вход</h1>
        <p style={{opacity:.7, marginTop:6}}>Почта и пароль</p>
        <div style={{display:'grid', gap:10, marginTop:16}}>
          <input placeholder="email" value={email} onChange={e=>setEmail(e.target.value)} style={{padding:'10px 12px', borderRadius:10, border:'1px solid #1f2937', background:'#0f172a', color:'#e5e7eb'}}/>
          <input type="password" placeholder="пароль" value={password} onChange={e=>setPassword(e.target.value)} style={{padding:'10px 12px', borderRadius:10, border:'1px solid #1f2937', background:'#0f172a', color:'#e5e7eb'}}/>
          {error && <div style={{color:'#fecaca'}}>⚠ {error}</div>}
          <button type="submit" style={{background:'linear-gradient(135deg,#22d3ee,#3b82f6)', color:'#001018', border:0, padding:'10px 14px', borderRadius:10, fontWeight:700, cursor:'pointer'}}>Войти</button>
        </div>
      </form>
    </main>
  )
}
