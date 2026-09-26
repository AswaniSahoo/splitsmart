"""SplitSmart - split group expenses fairly, via web, REST or MCP."""


def main() -> None:
    import os

    import uvicorn

    from splitsmart.api import create_app

    # Bind to localhost by default: the app has no authentication.
    host = os.environ.get("SPLITSMART_HOST", "127.0.0.1")
    port = int(os.environ.get("SPLITSMART_PORT", "8000"))
    uvicorn.run(create_app(), host=host, port=port)
