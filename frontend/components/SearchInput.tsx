'use client'
import { useEffect, useRef, useState } from 'react'
import { apiFetch } from '@/lib/api'
type Item = { sku:number; name:string; offer_id:string }
export default function SearchInput({onSelect}:{onSelect?:(i:Item)=>void}){
  const [q,setQ] = useState('')
  const [items,setItems] = useState<Item[]>([])
  const [open,setOpen] = useState(false)
  const box = useRef<HTMLDivElement|null>(null)
  useEffect(()=>{
    const id = setTimeout(async ()=>{
      if(q.trim().length<2){ setItems([]); return }
      const res = await apiFetch(`/search?q=${encodeURIComponent(q)}`)
      if(res.ok){ const data = await res.json(); setItems(data.items||[]); setOpen(true) }
    }, 250); return ()=>clearTimeout(id)
  },[q])
  useEffect(()=>{
    const h = (e:MouseEvent)=>{ if(box.current && !box.current.contains(e.target as any)) setOpen(false) }
    window.addEventListener('click', h); return ()=>window.removeEventListener('click', h)
  },[])
  return (<div ref={box} style={{position:'relative', minWidth:320}}>
    <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Поиск по SKU / названию / offer_id" style={{width:'100%', padding:'10px 12px', borderRadius:10, border:'1px solid #1f2937', background:'#0f172a', color:'#e5e7eb'}}/>
    {open && items.length>0 && (<div style={{position:'absolute', top:'110%', left:0, right:0, background:'#0b1220', border:'1px solid #1f2937', borderRadius:12, overflow:'hidden', zIndex:10}}>
      {items.map((it,idx)=>(<button key={idx} onClick={()=>{ onSelect?.(it); setOpen(false) }} style={{display:'flex', width:'100%', textAlign:'left', gap:8, padding:'10px 12px', background:'transparent', border:0, color:'#e5e7eb', cursor:'pointer'}}>
        <span style={{opacity:.7}}>{it.sku}</span><span>· {it.name}</span><span style={{marginLeft:'auto', opacity:.6}}>{it.offer_id}</span>
      </button>))}
    </div>)}
  </div>)
}
