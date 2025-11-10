'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const links = [
  { href: '/admin', label: 'Обзор' },
  { href: '/admin/accounts', label: 'Ozon аккаунты' },
  { href: '/admin/reports', label: 'Отчёты и каналы' },
  { href: '/admin/settings', label: 'Настройки' },
]

export default function AdminLayout({ children }: { children: React.ReactNode }){
  const pathname = usePathname()
  return (
    <div>
      <aside className="sidebar">
        <div style={{fontWeight:800, fontSize:18, marginBottom:12}}>Ozon Analytics</div>
        {links.map(l => (
          <Link key={l.href} href={l.href} className={pathname===l.href ? 'active' : ''}>{l.label}</Link>
        ))}
        <div style={{marginTop:16}}><Link href="/logout">Выйти</Link></div>
      </aside>
      <main className="main">
        {children}
      </main>
    </div>
  )
}
