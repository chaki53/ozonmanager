'use client'
import { useEffect, useState } from 'react'

export default function SettingsPage(){
  const [token, setToken] = useState('')
  const [chat, setChat] = useState('')
  const [syncSec, setSyncSec] = useState('10800')
  const [smtpHost, setSmtpHost] = useState('')
  const [smtpUser, setSmtpUser] = useState('')
  const [smtpPass, setSmtpPass] = useState('')
  const [smtpFrom, setSmtpFrom] = useState('')

  useEffect(()=>{
    const t = localStorage.getItem('jwt') || ''
    setToken(t)
    // Load existing settings (admin)
    fetch('/settings', { headers:{ 'Authorization':'Bearer '+t }}).then(r=>r.json()).then(items=>{
      const map = Object.fromEntries(items.map((x:any)=>[x.key,x.value]))
      setSyncSec(map.SYNC_PERIOD_SECONDS || '10800')
      setSmtpHost(map.SMTP_HOST || ''); setSmtpUser(map.SMTP_USER || ''); setSmtpPass(map.SMTP_PASSWORD || ''); setSmtpFrom(map.SMTP_FROM || '')
    }).catch(()=>{})
  }, [])

  async function saveTelegram(){
    const res = await fetch('/me/telegram', { method:'POST', headers:{ 'Content-Type':'application/json', 'Authorization':'Bearer '+token }, body: JSON.stringify({ telegram_chat_id: chat }) })
    alert(res.ok ? 'Сохранено' : 'Ошибка')
  }
  async function saveSettings(){
    const items = [
      { key:'SYNC_PERIOD_SECONDS', value: syncSec },
      { key:'SMTP_HOST', value: smtpHost },
      { key:'SMTP_USER', value: smtpUser },
      { key:'SMTP_PASSWORD', value: smtpPass },
      { key:'SMTP_FROM', value: smtpFrom },
    ]
    const res = await fetch('/settings', { method:'POST', headers:{ 'Content-Type':'application/json', 'Authorization':'Bearer '+token }, body: JSON.stringify(items) })
    alert(res.ok ? 'Настройки сохранены' : 'Ошибка сохранения')
  }

  return (
    <div className="container">
      <div className="header"><h1 className="h1">Настройки</h1></div>

      <div className="card" style={{marginTop:16}}>
        <div className="h2">Telegram: чат для уведомлений</div>
        <div className="grid grid-2">
          <input className="input" placeholder="chat_id" value={chat} onChange={e=>setChat(e.target.value)} />
          <button className="btn" onClick={saveTelegram}>Сохранить чат</button>
        </div>
      </div>

      <div className="card" style={{marginTop:16}}>
        <div className="h2">Автосинхронизация</div>
        <div className="grid grid-2">
          <input className="input" placeholder="SYNC_PERIOD_SECONDS" value={syncSec} onChange={e=>setSyncSec(e.target.value)} />
          <span className="badge">секунды</span>
        </div>
        <div style={{marginTop:12}}><button className="btn" onClick={saveSettings}>Сохранить</button></div>
      </div>

      <div className="card" style={{marginTop:16}}>
        <div className="h2">SMTP (для e‑mail отчётов)</div>
        <div className="grid grid-2">
          <input className="input" placeholder="SMTP_HOST" value={smtpHost} onChange={e=>setSmtpHost(e.target.value)} />
          <input className="input" placeholder="SMTP_USER" value={smtpUser} onChange={e=>setSmtpUser(e.target.value)} />
          <input className="input" placeholder="SMTP_PASSWORD" value={smtpPass} onChange={e=>setSmtpPass(e.target.value)} />
          <input className="input" placeholder='SMTP_FROM (например, "Ozon <noreply@domain>")' value={smtpFrom} onChange={e=>setSmtpFrom(e.target.value)} />
        </div>
        <div style={{marginTop:12}}><button className="btn" onClick={saveSettings}>Сохранить</button></div>
      </div>
    </div>
  )
}
