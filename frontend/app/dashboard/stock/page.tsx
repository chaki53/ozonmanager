'use client'
import { useEffect, useState } from 'react'

type Row = { account_id: string; warehouse_id: string; product_id: string; on_hand: number; dr7: number|null; doc_days: number|null }

export default function StockPage(){
  const [rows, setRows] = useState<Row[]>([])
  const [query, setQuery] = useState('')

  useEffect(() => {
    // TODO: fetch('/analytics/stock_overview', { headers: { Authorization: 'Bearer ...' } })
    setRows([])
  }, [])

  const filtered = rows.filter(r => [r.account_id,r.warehouse_id,r.product_id].join(' ').toLowerCase().includes(query.toLowerCase()))

  return (
    <main style={{padding:24}}>
      <h1>Запасы и покрытие (DoC)</h1>
      <p>Отображается последний срез по каждому SKU/складу и DR7 (средний дневной расход за 7 дней).</p>

      <div style={{display:'flex', gap:12, marginTop:8, flexWrap:'wrap'}}>
        <input placeholder="Поиск…" value={query} onChange={e=>setQuery(e.target.value)} />
        <a href="/dashboard">← назад к дашборду</a>
      </div>

      <div style={{overflow:'auto', marginTop:12}}>
        <table style={{minWidth:900, borderCollapse:'collapse'}}>
          <thead><tr>
            <th style={{textAlign:'left', padding:8, borderBottom:'1px solid #ddd'}}>Account</th>
            <th style={{textAlign:'left', padding:8, borderBottom:'1px solid #ddd'}}>Warehouse</th>
            <th style={{textAlign:'left', padding:8, borderBottom:'1px solid #ddd'}}>Product</th>
            <th style={{textAlign:'right', padding:8, borderBottom:'1px solid #ddd'}}>On hand</th>
            <th style={{textAlign:'right', padding:8, borderBottom:'1px solid #ddd'}}>DR7</th>
            <th style={{textAlign:'right', padding:8, borderBottom:'1px solid #ddd'}}>DoC (дней)</th>
          </tr></thead>
          <tbody>
            {filtered.map((r, i) => (
              <tr key={i} style={{background: r.doc_days!==null && r.doc_days<15 ? '#ffe5e5':'transparent'}}>
                <td style={{padding:8}}>…{r.account_id.slice(0,8)}</td>
                <td style={{padding:8}}>…{r.warehouse_id.slice(0,8)}</td>
                <td style={{padding:8}}>…{r.product_id.slice(0,8)}</td>
                <td style={{padding:8, textAlign:'right'}}>{r.on_hand}</td>
                <td style={{padding:8, textAlign:'right'}}>{r.dr7 ?? '-'}</td>
                <td style={{padding:8, textAlign:'right'}}>{r.doc_days ? r.doc_days.toFixed(1) : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p style={{marginTop:8, fontSize:12, opacity:.8}}>Красным выделены позиции, где покрытия &lt; 15 дней.</p>
    </main>
  )
}
