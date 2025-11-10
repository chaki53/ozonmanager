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
    setToken(t)
    refresh(t)
  }, [])

  async function refresh(tkn?: string) {
    try {
      const res = await fetch('/accounts', { headers: { 'Authorization': 'Bearer ' + (tkn || token) } })
      if (!res.ok) throw new Error(await res.text())
      setAccounts(await res.json())
    } catch (e) {
      console.error(e)
      alert('Не удалось получить аккаунты (нужен токен)')
    }
  }

  async function testKeys() {
    try {
      const res = await fetch('/accounts/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
        body: JSON.stringify({ ozon_client_id: clientId, ozon_api_key: apiKey })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data?.detail || 'auth failed')
      alert('OK: складов ' + data.warehouses)
    } catch (e:any) {
      alert('Ошибка проверки: ' + e.message)
    }
  }

  async function create() {
    try {
      const res = await fetch('/accounts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
        body: JSON.stringify({ name, ozon_client_id: clientId, ozon_api_key: apiKey, tz })
      })
      if (!res.ok) throw new Error(await res.text())
      setName(''); setClientId(''); setApiKey('')
      await refresh()
      alert('Аккаунт добавлен')
    } catch (e:any) {
      alert('Не удалось добавить: ' + e.message)
    }
  }

  async function del(id: string) {
    if (!confirm('Удалить аккаунт?')) return
    try {
      const res = await fetch('/accounts/' + id, { method: 'DELETE', headers: { 'Authorization': 'Bearer ' + token } })
      if (!res.ok) throw new Error(await res.text())
      await refresh()
    } catch (e:any) {
      alert('Ошибка удаления: ' + e.message)
    }
  }

  async function syncOne(id: string) {
    try {
      const res = await fetch('/sync/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
        body: JSON.stringify({ account_ids: [id], sales_days: 30 })
      })
      if (!res.ok) throw new Error(await res.text())
      alert('Синхронизация запущена')
    } catch (e:any) {
      alert('Не удалось запустить синк: ' + e.message)
    }
  }

  return (
    <main style={{padding:24, maxWidth:900, margin:'0 auto'}}>
      <h1>Озон аккаунты</h1>
      <section style={{marginTop:16, padding:16, border:'1px solid #ddd', borderRadius:12}}>
        <h3>Добавить аккаунт</h3>
        <div style={{display:'grid', gap:8}}>
          <input placeholder="Название" value={name} onChange={e=>setName(e.target.value)} />
          <input placeholder="Client-ID" value={clientId} onChange={e=>setClientId(e.target.value)} />
          <input placeholder="API-key" value={apiKey} onChange={e=>setApiKey(e.target.value)} />
          <input placeholder="Europe/Moscow" value={tz} onChange={e=>setTz(e.target.value)} />
        </div>
        <div style={{display:'flex', gap:8, marginTop:12}}>
          <button onClick={testKeys}>Проверить доступ</button>
          <button onClick={create}>Сохранить</button>
        </div>
      </section>

      <section style={{marginTop:24}}>
        <h3>Список аккаунтов</h3>
        <table style={{width:'100%', borderCollapse:'collapse'}}>
          <thead><tr>
            <th style={{textAlign:'left', padding:8, borderBottom:'1px solid #eee'}}>Название</th>
            <th style={{textAlign:'left', padding:8, borderBottom:'1px solid #eee'}}>TZ</th>
            <th style={{textAlign:'right', padding:8, borderBottom:'1px solid #eee'}}>Действия</th>
          </tr></thead>
          <tbody>
            {accounts.map(a => (
              <tr key={a.id}>
                <td style={{padding:8}}>{a.name}</td>
                <td style={{padding:8}}>{a.tz}</td>
                <td style={{padding:8, textAlign:'right'}}>
                  <button onClick={()=>syncOne(a.id)} style={{marginRight:8}}>Синхронизировать</button>
                  <button onClick={()=>del(a.id)} style={{color:'#b00'}}>Удалить</button>
                </td>
              </tr>
            ))}
            {accounts.length===0 && <tr><td colSpan={3} style={{padding:8, opacity:.6}}>Пока нет аккаунтов</td></tr>}
          </tbody>
        </table>
      </section>
    </main>
  )
}
