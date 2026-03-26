import os, uuid, mimetypes, urllib.request

base = "http://127.0.0.1:8001/api/files/upload?workspace_id=betterhealthcheck_com"
path = r"C:\Users\HP\Documents\LinkCraftor\tmp_upload_test.html"

boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
name = os.path.basename(path)
ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
data = open(path, "rb").read()

body = b""
body += (f"--{boundary}\r\n").encode()
body += (f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n').encode()
body += (f"Content-Type: {ctype}\r\n\r\n").encode()
body += data + b"\r\n"
body += (f"--{boundary}--\r\n").encode()

req = urllib.request.Request(base, data=body, method="POST")
req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
req.add_header("Content-Length", str(len(body)))

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        out = resp.read().decode("utf-8", "ignore")
        print("status:", resp.status)
        print(out)
except Exception as e:
    print("UPLOAD_ERROR:", repr(e))
