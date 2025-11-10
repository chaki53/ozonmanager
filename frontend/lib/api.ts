export const API = process.env.NEXT_PUBLIC_API_BASE || '';
function authHeaders(init: RequestInit = {}){
  const token = typeof window !== 'undefined' ? localStorage.getItem('jwt') : null;
  const headers = new Headers(init.headers || {});
  if(!headers.has('Content-Type') && init.body) headers.set('Content-Type','application/json');
  if(token) headers.set('Authorization', `Bearer ${token}`);
  return headers;
}
export async function apiFetch(path: string, init: RequestInit = {}){
  return fetch(`${API}${path}`, { ...init, headers: authHeaders(init), credentials: 'include' });
}
