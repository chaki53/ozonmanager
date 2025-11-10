import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl
  // guard /admin and /dashboard
  if (pathname.startsWith('/admin') || pathname.startsWith('/dashboard')) {
    const jwt = req.cookies.get('jwt')?.value
    if (!jwt) {
      const url = req.nextUrl.clone()
      url.pathname = '/login'
      return NextResponse.redirect(url)
    }
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/admin/:path*', '/dashboard/:path*'],
}
