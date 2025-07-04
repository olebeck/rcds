import hashlib

def is_hex(val: str) -> bool:
    return all([v in "0123456789abcdef" for v in val])

def rcd_entry(key, id):
    return f"key:{key}(0) id:{id}\n"

def name2id(name: str) -> str:
    return hashlib.sha1(name.encode("utf8")).hexdigest()[0:8].lower()
