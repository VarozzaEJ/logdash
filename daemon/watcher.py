import asyncio
import os
import json
import socket
from dotenv import load_dotenv
from models import LogEntry
from uploader import Uploader

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DOCKER_SOCKET = "/var/run/docker.sock"
WATCHED_SERVICE = "logdash-dummy-app-1"

def parse_level(line: str) -> str:
    upper = line.upper()
    if "ERROR" in upper:
        return "ERROR"
    if "WARN" in upper:
        return "WARN"
    return "INFO"

def get_container_id(name: str) -> str:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(DOCKER_SOCKET)
    sock.send(b"GET /containers/json HTTP/1.0\r\nHost: localhost\r\n\r\n")
    data = b""
    while chunk := sock.recv(4096):
        data += chunk
    sock.close()
    body = data.split(b"\r\n\r\n", 1)[1]
    containers = json.loads(body)
    for c in containers:
        for n in c.get("Names", []):
            if name in n.lstrip("/"):
                return c["Id"]
    return None

def tail_container(container_id: str, service_name: str, uploader: Uploader):
    print(f"Watching container: {service_name}")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(DOCKER_SOCKET)
    request = (
        f"GET /containers/{container_id}/logs"
        f"?follow=1&stdout=1&stderr=1&tail=0 HTTP/1.0\r\n"
        f"Host: localhost\r\n\r\n"
    )
    sock.send(request.encode())

    buffer = b""
    while b"\r\n\r\n" not in buffer:
        buffer += sock.recv(1)

    while True:
        header = b""
        while len(header) < 8:
            chunk = sock.recv(8 - len(header))
            if not chunk:
                return
            header += chunk
        size = int.from_bytes(header[4:8], "big")
        payload = b""
        while len(payload) < size:
            chunk = sock.recv(size - len(payload))
            if not chunk:
                return
            payload += chunk
        line = payload.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        entry = LogEntry(
            service=service_name,
            level=parse_level(line),
            message=line,
        )
        uploader.enqueue(entry)
        print(f"[{entry.level}] {entry.service}: {entry.message}")

async def main():
    print("Logdash daemon starting...")
    uploader = Uploader(SUPABASE_URL, SUPABASE_KEY)

    container_id = get_container_id(WATCHED_SERVICE)
    if not container_id:
        print(f"Container '{WATCHED_SERVICE}' not found. Is it running?")
        return

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, tail_container, container_id, WATCHED_SERVICE, uploader)

    await uploader.run()

if __name__ == "__main__":
    asyncio.run(main())