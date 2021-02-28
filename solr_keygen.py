import base64
import secrets
import hashlib

# The latest Solr doc claims the Basic Authentication Plugin's password storage format is
# sha256(password+salt): https://lucene.apache.org/solr/guide/8_8/basic-authentication-plugin.html
# This is WRONG.
# It's actually sha256(sha256(salt+password))
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

# The format in JSON is
# "credentials":{"[username]":"[base64(sha256(sha256(salt+password)))] [base64(salt)]"},
print(base64.b64encode(btPass).decode('utf-8') + " " + base64.b64encode(salt).decode('ascii'))