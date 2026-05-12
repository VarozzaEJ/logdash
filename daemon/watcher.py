import asyncio
import os
import json
import socket
import re
from dotenv import load_dotenv
from models import LogEntry
from uploader import Uploader

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DOCKER_SOCKET = "/var/run/docker.sock"
IGNORED_CONTAINERS = {"logdash-daemon-1"}

def docker_request(path: str) -> bytes:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(DOCKER_SOCKET)
    sock.send(f"GET {path} HTTP/1.0\r\nHost: localhost\r\n\r\n".encode())
    data = b""
    while chunk := sock.recv(4096):
        data += chunk
    sock.close()
    return data.split(b"\r\n\r\n", 1)[1]

def get_running_containers() -> list[dict]:
    body = docker_request("/containers/json")
    containers = json.loads(body)
    result = []
    for c in containers:
        name = c["Names"][0].lstrip("/")
        if name not in IGNORED_CONTAINERS:
            result.append({"id": c["Id"], "name": name})
    return result

LOG_LEVEL_PATTERN = re.compile(
    r'\b(DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL)\b',
    re.IGNORECASE
)

def parse_level(line: str) -> str:
    match = LOG_LEVEL_PATTERN.search(line)
    if not match:
        return "INFO"
    level = match.group(1).upper()
    if level in ("WARN", "WARNING"):
        return "WARN"
    if level in ("CRITICAL", "FATAL"):
        return "ERROR"
    if level == "DEBUG":
        return "INFO"
    return level

def tail_container(container: dict, uploader: Uploader):
    container_id = container["id"]
    service_name = container["name"]
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
        print(f"[{entry.level}] {service_name}: {entry.message}")

async def watch_loop(uploader: Uploader, loop: asyncio.AbstractEventLoop):
    watched = set()
    while True:
        containers = get_running_containers()
        for container in containers:
            if container["id"] not in watched:
                watched.add(container["id"])
                loop.run_in_executor(
                    None, tail_container, container, uploader
                )
        await asyncio.sleep(5)

async def main():
    print("Logdash daemon starting...")
    uploader = Uploader(SUPABASE_URL, SUPABASE_KEY)
    loop = asyncio.get_event_loop()

    await asyncio.gather(
        watch_loop(uploader, loop),
        uploader.run()
    )

if __name__ == "__main__":
    asyncio.run(main())