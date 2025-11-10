'use client'
import { useEffect, useState } from 'react'
import ReportCard from '@/components/ReportCard'
import SearchInput from '@/components/SearchInput'
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd'

type Widget = { key:string; title:string; type:'pie'|'bar'|'line'; enabled:boolean }
const initial: Widget[] = [
  { key:'sales', title:'Продажи: сводка', type:'line', enabled:true },
  { key:'stock', title:'Запасы и DoC', type:'pie', enabled:true },
  { key:'abc', title:'ABC/XYZ', type:'pie', enabled:true },
  { key:'finance', title:'Финансовые транзакции', type:'bar', enabled:true },
  { key:'ship', title:'Отгрузки (FBO/FBS)', type:'bar', enabled:true },
]
export default function Dashboard(){
  const [widgets,setWidgets] = useState<Widget[]>(()=>{ if(typeof window==='undefined') return initial; try{ return JSON.parse(localStorage.getItem('widgets')||'') || initial }catch{ return initial } })
  const [dateFrom,setDateFrom] = useState<string>('2025-10-11')
  const [dateTo,setDateTo] = useState<string>('2025-11-10')
  const [data,setData] = useState<any>({})
  const [picked,setPicked] = useState<any>(null)
  useEffect(()=>{ localStorage.setItem('widgets', JSON.stringify(widgets)) },[widgets])
  useEffect(()=>{
    setData({
      sales:[{name:'10-01', value:200},{name:'10-05', value:260},{name:'10-10', value:400},{name:'10-15', value:380},{name:'10-20', value:450}],
      stock:[{name:'Склад А', value:500, share:.5},{name:'Склад Б', value:300, share:.3},{name:'Склад В', value:200, share:.2}],
      abc:[{name:'A', value:20, share:.2},{name:'B', value:30, share:.3},{name:'C', value:50, share:.5}],
      finance:[{name:'Платежи', value:800},{name:'Комиссии', value:120},{name:'Доставка', value:90}],
      ship:[{name:'FBO', value:600},{name:'FBS', value:400}],
    })
  },[dateFrom,dateTo])
  function onDragEnd(result: DropResult){
    if(!result.destination) return
    const next = Array.from(widgets); const [removed] = next.splice(result.source.index,1); next.splice(result.destination.index,0,removed); setWidgets(next)
  }
  return (<main style={{padding:24, color:'#e5e7eb', background:'#0b0f14', minHeight:'100vh'}}>
    <div style={{display:'flex', gap:12, alignItems:'center', justifyContent:'space-between'}}>
      <h1 style={{margin:0}}>Дашборд</h1>
      <div style={{display:'flex', gap:12, alignItems:'center'}}>
        <SearchInput onSelect={(it)=>setPicked(it)} />
        <a href="/settings" style={{padding:'8px 12px', border:'1px solid #1f2937', borderRadius:10}}>Настройки</a>
      </div>
    </div>
    <div style={{margin:'12px 0', display:'flex', gap:12, alignItems:'center'}}>
      <label>с: <input type="date" value={dateFrom} onChange={e=>setDateFrom(e.target.value)} /></label>
      <label>по: <input type="date" value={dateTo} onChange={e=>setDateTo(e.target.value)} /></label>
      {picked && <span style={{opacity:.8}}>Фильтр по товару: <b>{picked.name}</b> (SKU {picked.sku})</span>}
    </div>
    <DragDropContext onDragEnd={onDragEnd}>
      <Droppable droppableId="list">{(provided)=>(
        <div ref={provided.innerRef} {...provided.droppableProps} style={{display:'grid', gap:16}}>
          {widgets.filter(w=>w.enabled).map((w,i)=>(
            <Draggable key={w.key} draggableId={w.key} index={i}>{(p)=>(
              <div ref={p.innerRef} {...p.draggableProps} {...p.dragHandleProps}>
                <ReportCard title={w.title} type={w.type} data={data[w.key]||[]} />
              </div>
            )}</Draggable>
          ))}
          {provided.placeholder}
        </div>
      )}</Droppable>
    </DragDropContext>
  </main>)
}
