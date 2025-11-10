'use client'
import { useEffect, useState } from 'react'
type Pref = { report_key: string; show_on_dashboard: boolean; send_to_telegram: boolean; send_to_email: boolean }
const CATALOG = [
  { key: 'sales_summary', title: 'Продажи: сводка' },
  { key: 'stock_doc', title: 'Запасы и DoC' },
  { key: 'abcxyz', title: 'ABC/XYZ' },
  { key: 'transactions', title: 'Финансовые транзакции' },
  { key: 'postings', title: 'Отгрузки (FBO/FBS)' },
]

export default function ReportsPage(){
  const [prefs, setPrefs] = useState<Pref[]>([])
  const [token, setToken] = useState('')

  useEffect(()=>{
    const t = localStorage.getItem('jwt') || ''
    setToken(t)
    fetch('/reports/preferences', { headers: { 'Authorization': 'Bearer ' + t }})
      .then(r=>r.json()).then(setPrefs).catch(()=>setPrefs(CATALOG.map(c=>({report_key:c.key,show_on_dashboard:true,send_to_email:false,send_to_telegram:false}))))
  }, [])

  function toggle(key: string, fld: keyof Pref, v: boolean){
    setPrefs(prev => {
      const next = prev.slice()
      const i = next.findIndex(x=>x.report_key===key)
      if (i>=0) next[i] = { ...next[i], [fld]: v }
      else next.push({ report_key:key, show_on_dashboard:false, send_to_email:false, send_to_telegram:false, [fld]: v } as any)
      return next
    })
  }

  async function save(){
    const res = await fetch('/reports/preferences', { method:'POST', headers:{ 'Content-Type':'application/json','Authorization':'Bearer '+token }, body: JSON.stringify(prefs) })
    alert(res.ok ? 'Сохранено' : 'Ошибка сохранения')
  }

  return (
    <div className="container">
      <div className="header"><h1 className="h1">Отчёты и каналы</h1></div>
      <div className="card" style={{marginTop:16}}>
        <table className="table">
          <thead><tr><th>Отчёт</th><th>На дашборде</th><th>Telegram</th><th>E‑mail</th></tr></thead>
          <tbody>
            {CATALOG.map(c => {
              const p = prefs.find(x=>x.report_key===c.key) || {report_key:c.key, show_on_dashboard:false, send_to_email:false, send_to_telegram:false}
              return (
                <tr key={c.key}>
                  <td>{c.title}</td>
                  <td><input type="checkbox" checked={p.show_on_dashboard} onChange={e=>toggle(c.key,'show_on_dashboard',e.target.checked)} /></td>
                  <td><input type="checkbox" checked={p.send_to_telegram} onChange={e=>toggle(c.key,'send_to_telegram',e.target.checked)} /></td>
                  <td><input type="checkbox" checked={p.send_to_email} onChange={e=>toggle(c.key,'send_to_email',e.target.checked)} /></td>
                </tr>
              )
            })}
          </tbody>
        </table>
        <div style={{marginTop:12}}><button className="btn" onClick={save}>Сохранить</button></div>
      </div>
    </div>
  )
}
