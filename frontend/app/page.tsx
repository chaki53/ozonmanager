export default function Home(){ return (<main style={{padding:24}}>
  <h1>Ozon Manager</h1>
  <ul>
    <li><a href="/login">Вход</a></li>
    <li><a href="/dashboard">Дашборд</a></li>
    <li><a href="/settings">Настройки аккаунта</a></li>
    <li><a href="/admin/accounts">Админ: Кабинеты</a></li>
    <li><a href="/admin/sync">Админ/Менеджер: Синхронизация</a></li>
  </ul>
</main>) }
