'use client'
import { useEffect, useState } from 'react'

type Pref = {
  report_key: string
  show_on_dashboard: boolean
  send_to_telegram: boolean
  send_to_email: boolean
}

const CATALOG: {key: string, title: string}[] = [
  { key: 'sales_summary', title: 'Продажи: сводка' },
  { key: 'stock_doc', title: 'Запасы и DoC' },
  { key: 'abcxyz', title: 'ABC/XYZ' },
  { key: 'transactions', title: 'Финансовые транзакции' },
  { key: 'postings', title: 'Отгрузки (FBO/FBS)' },
]

export default function Dashboard() {
  const [prefs, setPrefs] = useState<Pref[]>([])

  useEffect(() => {
    // TODO: fetch /reports/preferences с токеном
    setPrefs(CATALOG.map(c => ({report_key: c.key, show_on_dashboard: true, send_to_email: false, send_to_telegram: false})))
  }, [])

  return (
    <main style={{ padding: 24 }}>
      <h1>Дашборд</h1>
      <section style={{ marginTop: 16 }}>
        <h2>Показывать на дашборде</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(1, minmax(0, 1fr))', gap: 8 }}>
          {CATALOG.map(item => {
            const p = prefs.find(x => x.report_key === item.key)
            const visible = p?.show_on_dashboard
            if (!visible) return null
            return (
              <div key={item.key} style={{ padding: 16, border: '1px solid #ddd', borderRadius: 12 }}>
                <b>{item.title}</b>
                <div style={{ marginTop: 8, fontSize: 12, opacity: 0.8 }}>Отчёт {item.key} (демо‑виджет)</div>
              </div>
            )
          })}
        </div>
      </section>

      <section style={{ marginTop: 24 }}>
        <h2>Настройки отображения и каналов</h2>
        <div style={{ display: 'grid', gap: 8 }}>
          {CATALOG.map(c => {
            const p = prefs.find(x => x.report_key === c.key) || {report_key: c.key, show_on_dashboard: false, send_to_email: false, send_to_telegram: false}
            return (
              <div key={c.key} style={{ padding: 12, border: '1px dashed #ccc', borderRadius: 12 }}>
                <b>{c.title}</b>
                <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
                  <label><input type="checkbox" checked={p.show_on_dashboard} onChange={e => {
                    const v = e.target.checked
                    setPrefs(prev => prev.map(x => x.report_key===c.key?{...x, show_on_dashboard:v}:x))
                  }}/> На дашборде</label>
                  <label><input type="checkbox" checked={p.send_to_telegram} onChange={e => {
                    const v = e.target.checked
                    setPrefs(prev => prev.map(x => x.report_key===c.key?{...x, send_to_telegram:v}:x))
                  }}/> В Telegram</label>
                  <label><input type="checkbox" checked={p.send_to_email} onChange={e => {
                    const v = e.target.checked
                    setPrefs(prev => prev.map(x => x.report_key===c.key?{...x, send_to_email:v}:x))
                  }}/> На e‑mail</label>
                </div>
              </div>
            )
          })}
        </div>
        <button style={{ marginTop: 12, padding: '8px 12px', borderRadius: 8, border: '1px solid #333' }}
          onClick={() => {
            // TODO: POST /reports/preferences с токеном
            alert('Сохранено (демо)')
          }}>Сохранить настройки</button>
      </section>
    </main>
  )
}
