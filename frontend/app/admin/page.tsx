export default function AdminPage(){
  return (
    <div className="container">
      <div className="header">
        <h1 className="h1">Админ-панель</h1>
        <span className="badge">роль: admin/manager</span>
      </div>
      <div className="grid grid-3" style={{marginTop:16}}>
        <div className="card"><div className="h2">Быстрый старт</div><p>Добавьте Ozon аккаунт и запустите синхронизацию. Затем настройте отчёты и каналы.</p></div>
        <div className="card"><div className="h2">Статус</div><p className="mono">docker compose ps<br/>/healthz</p></div>
        <div className="card"><div className="h2">Поддержка</div><p>Вопросы? Напишите нам.</p></div>
      </div>
    </div>
  )
}
