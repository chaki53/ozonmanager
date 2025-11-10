'use client'
import { ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, LineChart, Line } from 'recharts'
const COLORS = ['#22d3ee','#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6']
export default function ReportCard({title, subtitle, type='pie', data=[]}:{title:string, subtitle?:string, type?:'pie'|'bar'|'line', data:any[]}){
  return (<div style={{background:'#111827',border:'1px solid #1f2937',borderRadius:16,padding:16}}>
    <div style={{display:'flex',justifyContent:'space-between',alignItems:'baseline'}}>
      <h3 style={{margin:0}}>{title}</h3>{subtitle && <span style={{opacity:.6,fontSize:12}}>{subtitle}</span>}
    </div>
    <div style={{height:220}}>
      <ResponsiveContainer width="100%" height="100%">
        {type === 'pie' ? (<PieChart>
          <Pie data={data} dataKey="value" nameKey="name" outerRadius={80} label={(e)=>`${e.name} ${Math.round((e.percent||0)*100)}%`}>
            {data.map((_:any, i:number)=>(<Cell key={i} fill={COLORS[i % COLORS.length]} />))}
          </Pie><Tooltip /><Legend />
        </PieChart>) : type === 'line' ? (<LineChart data={data}><XAxis dataKey="name" /><YAxis /><Tooltip /><Legend /><Line type="monotone" dataKey="value" /></LineChart>) : (
          <BarChart data={data}><XAxis dataKey="name" /><YAxis /><Tooltip /><Legend /><Bar dataKey="value" /></BarChart>
        )}
      </ResponsiveContainer>
    </div>
    <ul style={{margin:0,paddingLeft:18,opacity:.85}}>
      {data.map((d:any,i:number)=>(<li key={i}>{d.name}: <b>{d.value}</b>{typeof d.share==='number' ? ` (${Math.round(d.share*100)}%)` : ''}</li>))}
    </ul>
  </div>)
}
