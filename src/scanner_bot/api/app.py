from __future__ import annotations

import os
from fastapi import FastAPI

app = FastAPI(title="Scanner API")


@app.get("/ping")
def ping() -> dict:
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))

    # Import string keeps reload happy
    uvicorn.run("scanner_bot.api.app:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()
