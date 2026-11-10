"""Resumable upload of a large file to Google Drive (v3) through the agent proxy.

The proxy injects the OAuth bearer token for www.googleapis.com; the header
value sent here is only a placeholder that the proxy overwrites.
"""
import json, os, sys, time, urllib.request, urllib.error

path, name = sys.argv[1], sys.argv[2]
parent = sys.argv[3] if len(sys.argv) > 3 else None
size = os.path.getsize(path)
CHUNK = 64 * 1024 * 1024  # multiple of 256 KiB
AUTH = {"Authorization": "Bearer proxy-injected"}
state_file = path + ".upload_session"


def req(url, method="GET", data=None, headers=None):
    r = urllib.request.Request(url, data=data, method=method, headers={**AUTH, **(headers or {})})
    try:
        with urllib.request.urlopen(r, timeout=600) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def start_session():
    meta = {"name": name, "mimeType": "video/mp4"}
    if parent:
        meta["parents"] = [parent]
    st, h, body = req(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true&fields=id,name,size,webViewLink",
        "POST", json.dumps(meta).encode(),
        {"Content-Type": "application/json; charset=UTF-8", "X-Upload-Content-Type": "video/mp4",
         "X-Upload-Content-Length": str(size)})
    if st != 200:
        raise SystemExit(f"session start failed {st}: {body[:500]!r}")
    loc = h.get("Location") or h.get("location")
    open(state_file, "w").write(loc)
    return loc


def committed(loc):
    st, h, body = req(loc, "PUT", b"", {"Content-Range": f"bytes */{size}", "Content-Length": "0"})
    if st in (200, 201):
        return size, body
    if st == 308:
        rng = h.get("Range") or h.get("range")
        return (int(rng.split("-")[1]) + 1 if rng else 0), None
    if st == 404:
        return None, None
    raise RuntimeError(f"status query {st}: {body[:300]!r}")


loc = open(state_file).read().strip() if os.path.exists(state_file) else start_session()
off, done = committed(loc)
if off is None:
    loc = start_session(); off, done = 0, None
t0 = time.time(); start_off = off
with open(path, "rb") as f:
    while done is None:
        f.seek(off)
        chunk = f.read(CHUNK)
        end = off + len(chunk) - 1
        for attempt in range(6):
            try:
                st, h, body = req(loc, "PUT", chunk, {"Content-Range": f"bytes {off}-{end}/{size}",
                                                     "Content-Length": str(len(chunk))})
                break
            except Exception as e:  # network hiccup: ask server what it has, then retry
                print("retry", attempt, e, flush=True); time.sleep(2 ** attempt)
                o2, d2 = committed(loc)
                if d2 is not None:
                    st, body = 200, d2; break
                off = o2; f.seek(off); chunk = f.read(CHUNK); end = off + len(chunk) - 1
        else:
            raise SystemExit("upload failed after retries")
        if st in (200, 201):
            done = body
        elif st == 308:
            rng = h.get("Range") or h.get("range")
            off = int(rng.split("-")[1]) + 1 if rng else 0
            rate = (off - start_off) / max(1, time.time() - t0) / 1e6
            print(f"{off/1e6:.0f}/{size/1e6:.0f} MB  {rate:.1f} MB/s", flush=True)
        else:
            raise SystemExit(f"chunk failed {st}: {body[:500]!r}")
os.remove(state_file)
print("DONE", done.decode())
