import base64
import secrets
import hashlib

password = secrets.token_urlsafe(16)
salt = secrets.token_bytes(32)

h = hashlib.sha256()
h.update(salt)
h.update(password.encode('utf-8'))
btPass = h.digest()
h = hashlib.sha256()
h.update(btPass)
btPass = h.digest()

print("Password: " + password)
print(base64.b64encode(btPass).decode('utf-8') + " " + base64.b64encode(salt).decode('ascii'))