export const API = process.env.NEXT_PUBLIC_API_BASE || '';

export async function apiFetch(path: string, init: RequestInit = {}){
  const token = typeof window !== 'undefined' ? localStorage.getItem('jwt') : null;
  const headers = new Headers(init.headers || {});
  if(!headers.has('Content-Type') && init.body) headers.set('Content-Type','application/json');
  if(token) headers.set('Authorization', `Bearer ${token}`);
  return fetch(`${API}${path}`, { ...init, headers, credentials: 'include' });
}
