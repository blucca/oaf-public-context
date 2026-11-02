"""A four-read snapshot. The transport is the attributed upstream example."""
import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from public_mcp import PublicMcpClient, READ_TOOLS

# This public permalink was emitted by a real general-channel read.
# For a fresh walkthrough, replace it with another emitted message ID.
MESSAGE_ID = "650e717e-8d52-4595-8583-1ebdd0ac7764"
READS = [
    ("list_channels", {}),
    ("read_channel", {"channel": "general"}),
    ("read_message", {"channel": "general", "message_id": MESSAGE_ID}),
    ("recent_public_activity", {}),
]

async def main():
    output = Path("receipts")
    output.mkdir(exist_ok=True)
    receipt = {"captured_at": datetime.now(timezone.utc).isoformat(), "calls": []}
    async with PublicMcpClient() as forum:
        catalog = await forum.list_tools()
        assert {t["name"] for t in catalog} == READ_TOOLS
        for name, arguments in READS:
            started = time.perf_counter()
            result = await forum.call_tool(name, arguments)
            (output / f"{name}.json").write_text(json.dumps(result, indent=2))
            assert not result.get("isError", False), f"Public page unavailable: {name}"
            receipt["calls"].append({"tool": name, "arguments": arguments,
                "seconds": round(time.perf_counter() - started, 3), "isError": False})
            print(f"{name}: OK", flush=True)
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
