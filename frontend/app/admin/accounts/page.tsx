'use client'
import { useEffect, useState } from 'react'

type Account = { id: string; name: string; tz: string }

export default function AdminAccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [name, setName] = useState('')
  const [clientId, setClientId] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [tz, setTz] = useState('Europe/Moscow')
  const [token, setToken] = useState('')

  useEffect(() => {
    const t = localStorage.getItem('jwt') || ''
    setToken(t); refresh(t)
  }, [])

  async function refresh(tkn?: string) {
    const res = await fetch('/accounts', { headers: { 'Authorization': 'Bearer ' + (tkn || token) } })
    if (res.ok) setAccounts(await res.json())
  }

  async function testKeys() {
    const res = await fetch('/accounts/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
      body: JSON.stringify({ ozon_client_id: clientId, ozon_api_key: apiKey })
    })
    const data = await res.json()
    alert(res.ok ? ('OK: складов ' + data.warehouses) : ('Ошибка: ' + (data?.detail || 'auth failed')))
  }

  async function create() {
    const res = await fetch('/accounts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
      body: JSON.stringify({ name, ozon_client_id: clientId, ozon_api_key: apiKey, tz })
    })
    if (res.ok){ setName(''); setClientId(''); setApiKey(''); refresh(); } else { alert('Не удалось сохранить') }
  }

  async function del(id: string) {
    if (!confirm('Удалить аккаунт?')) return
    const res = await fetch('/accounts/' + id, { method: 'DELETE', headers: { 'Authorization': 'Bearer ' + token } })
    if (res.ok) refresh()
  }

  async function syncOne(id: string) {
    const res = await fetch('/sync/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
      body: JSON.stringify({ account_ids: [id], sales_days: 30 })
    })
    alert(res.ok ? 'Синхронизация запущена' : 'Ошибка запуска синка')
  }

  return (
    <div className="container">
      <div className="header"><h1 className="h1">Ozon аккаунты</h1></div>

      <div className="card" style={{marginTop:16}}>
        <div className="h2">Добавить аккаунт</div>
        <div className="grid grid-2">
          <input className="input" placeholder="Название (например, Main Ozon)" value={name} onChange={e=>setName(e.target.value)} />
          <input className="input" placeholder="Часовой пояс (Europe/Moscow)" value={tz} onChange={e=>setTz(e.target.value)} />
          <input className="input" placeholder="Client-ID" value={clientId} onChange={e=>setClientId(e.target.value)} />
          <input className="input" placeholder="API-key" value={apiKey} onChange={e=>setApiKey(e.target.value)} />
        </div>
        <div style={{display:'flex', gap:8, marginTop:12}}>
          <button className="btn sec" onClick={testKeys}>Проверить доступ</button>
          <button className="btn" onClick={create}>Сохранить</button>
        </div>
      </div>

      <div className="card" style={{marginTop:16}}>
        <div className="h2">Список аккаунтов</div>
        <table className="table">
          <thead><tr><th>Название</th><th>TZ</th><th style={{textAlign:'right'}}>Действия</th></tr></thead>
          <tbody>
            {accounts.map(a => (
              <tr key={a.id}>
                <td>{a.name}</td>
                <td>{a.tz}</td>
                <td style={{textAlign:'right'}}>
                  <button className="btn sec" onClick={()=>syncOne(a.id)} style={{marginRight:8}}>Синхронизировать</button>
                  <button className="btn sec" onClick={()=>del(a.id)} style={{borderColor:'#b91c1c', color:'#fecaca'}}>Удалить</button>
                </td>
              </tr>
            ))}
            {accounts.length===0 && <tr><td colSpan={3} style={{opacity:.6}}>Пока нет аккаунтов</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}
