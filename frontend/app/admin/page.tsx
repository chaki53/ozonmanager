export default function AdminPage() {
  return (
    <main style={{ padding: 24 }}>
      <h1>Admin Panel</h1>
      <p>Здесь будет управление пользователями, ролями и аккаунтами Ozon.</p>
      <ul style={{marginTop:16}}>
        <li><a href="/admin/accounts">→ Управление аккаунтами Ozon</a></li>
        <li><a href="/dashboard">→ Дашборд и отчёты</a></li>
      </ul>
    </main>
  );
}
