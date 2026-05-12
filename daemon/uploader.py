import asyncio
from supabase import create_client, Client
from models import LogEntry

class Uploader:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)
        self.queue: list[LogEntry] = []

    def enqueue(self, entry: LogEntry):
        self.queue.append(entry)

    async def flush(self):
        if not self.queue:
            return
        batch = self.queue.copy()
        self.queue.clear()
        try:
            self.client.table("logs").insert(
                [entry.to_dict() for entry in batch]
            ).execute()
            print(f"Uploaded {len(batch)} log(s)")
        except Exception as e:
            print(f"Upload failed: {e}")

    async def run(self):
        while True:
            await asyncio.sleep(2)
            await self.flush()