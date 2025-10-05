import os
from typing import Optional
import httpx


async def upload_file_async(file_path: str, provider: str = "auto", timeout: int = 600) -> Optional[str]:
    """Upload a file to a public file host and return the URL.

    Providers:
    - auto: try 0x0.st then transfer.sh
    - 0x0: https://0x0.st (POST multipart)
    - transfer: https://transfer.sh (PUT stream)
    """
    filename = os.path.basename(file_path)

    async with httpx.AsyncClient(timeout=timeout) as client:
        # Helper: 0x0.st
        async def try_0x0() -> Optional[str]:
            url = "https://0x0.st"
            try:
                with open(file_path, "rb") as f:
                    files = {"file": (filename, f)}
                    r = await client.post(url, files=files)
                if r.status_code == 200 and r.text.strip():
                    return r.text.strip()
            except Exception:
                pass
            return None

        # Helper: transfer.sh
        async def try_transfer() -> Optional[str]:
            try:
                with open(file_path, "rb") as f:
                    r = await client.put(f"https://transfer.sh/{filename}", content=f)
                if r.status_code in (200, 201) and r.text.strip():
                    return r.text.strip()
            except Exception:
                pass
            return None

        if provider == "0x0":
            return await try_0x0()
        if provider == "transfer":
            return await try_transfer()

        # auto
        url = await try_0x0()
        if url:
            return url
        return await try_transfer()