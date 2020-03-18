from sanic import Sanic
import sanic.response

import asyncio
import os

import os
import tempfile
from contextlib import contextmanager

import json

TEMP_FILE = "/tmp/bluebell.json"


@contextmanager
def temp_fifo():
    """Context Manager for creating named pipes with temporary names."""
    tmpdir = tempfile.mkdtemp()
    filename = os.path.join(tmpdir, 'fifo')  # Temporary filename
    os.mkfifo(filename)  # Create FIFO
    try:
        yield filename
    finally:
        os.unlink(filename)  # Remove file
        os.rmdir(tmpdir)  # Remove directory


app = Sanic(name="bluebell")
app.config.RESPONSE_TIMEOUT = 9999
# scrapy crawl WorkshopListing -a game_id=440310 -t json -p {fifo_file}
@app.route("/")
async def test(request):
    return sanic.response.json({"hello": "world"})


@app.route("/<game_id>/levels")
async def dir(request, game_id):
    # await asyncio.sleep(5)
    os.unlink(TEMP_FILE)
    cmd = f"scrapy crawl WorkshopListing -a game_id={game_id} -o {TEMP_FILE}"
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    await proc.communicate()
    with open(TEMP_FILE, "r") as f:
        return sanic.response.json(json.loads(f.read()))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
