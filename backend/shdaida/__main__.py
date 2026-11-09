"""Run the SHAIDA API: ``python -m shdaida`` from the backend directory."""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.environ.get("SHAIDA_HOST", "127.0.0.1")
    port = int(os.environ.get("SHAIDA_PORT", "8000"))
    uvicorn.run("shdaida.api:app", host=host, port=port, reload=False, log_level="info")


if __name__ == "__main__":
    main()
