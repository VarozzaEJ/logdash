import asyncio
from supabase import create_client, Client
from models import LogEntry

MAX_RETRIES = 3
RETRY_DELAY = 1.0

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

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                self.client.table("logs").insert(
                    [entry.to_dict() for entry in batch]
                ).execute()
                print(f"Uploaded {len(batch)} log(s)")
                return
            except Exception as e:
                print(f"Upload attempt {attempt}/{MAX_RETRIES} failed: {e}")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAY * attempt)

        print(f"Dropped {len(batch)} log(s) after {MAX_RETRIES} failed attempts")

    async def run(self):
        while True:
            await asyncio.sleep(2)
            await self.flush()