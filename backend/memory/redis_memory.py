import redis, os, json

r = redis.from_url(os.getenv("REDIS_URL"))

def save_turn(session_id, msg):
    key = f"session:{session_id}"
    r.lpush(key, json.dumps(msg))
    r.ltrim(key, 0, 9)

def get_history(session_id):
    data = r.lrange(f"session:{session_id}", 0, 9)
    return [json.loads(x) for x in data]