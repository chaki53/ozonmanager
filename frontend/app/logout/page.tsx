'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function LogoutPage(){
  const router = useRouter()
  useEffect(()=>{
    // expire cookie and clear localStorage
    document.cookie = 'jwt=; Max-Age=0; path=/'
    localStorage.removeItem('jwt')
    router.replace('/login')
  }, [router])
  return <main style={{padding:24}}>Выход…</main>
}
