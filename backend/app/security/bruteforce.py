import time
import redis

# Use Redis DB 1 to separate from app cache
r = redis.from_url("redis://redis:6379/1", decode_responses=True)

WINDOW_SEC = 10*60   # 10 minutes sliding window
SOFT_LIMIT = 5       # after 5 attempts add delays
HARD_LIMIT = 10      # after 10 attempts lock for BAN_SEC
BAN_SEC = 15*60      # 15 minutes ban

def _key(ip: str, user: str) -> str:
    user = (user or '').lower().strip()
    return f"bf:{ip}:{user}"

def check_or_ban(ip: str, user: str):
    k = _key(ip, user)
    cnt = int(r.get(k) or 0)
    if r.get(k + ":ban"):
        ttl = r.ttl(k + ":ban")
        return False, f"Too many attempts. Try again in {ttl if ttl>0 else BAN_SEC}s"
    if cnt >= HARD_LIMIT:
        r.set(k + ":ban", "1", ex=BAN_SEC)
        return False, "Account temporarily locked due to many failed logins"
    if cnt >= SOFT_LIMIT:
        delay = min(8, 2 ** (cnt - SOFT_LIMIT))
        time.sleep(delay)
    return True, None

def register_failure(ip: str, user: str):
    k = _key(ip, user)
    p = r.pipeline()
    p.incr(k, 1)
    p.expire(k, WINDOW_SEC)
    p.execute()

def register_success(ip: str, user: str):
    k = _key(ip, user)
    r.delete(k); r.delete(k + ":ban")
