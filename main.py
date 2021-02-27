from sanic import Sanic
import sanic.response

import asyncio
import os

import os
import tempfile
from contextlib import contextmanager
import shutil
from sanic.exceptions import ServerError

import json

TEMP_FILE = "bluebell.json"
TEMP_DIR = "/tmp/bluebellws"


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
    if not (os.path.exists(TEMP_DIR)):
        os.mkdir(TEMP_DIR)
    abs_file = f"{TEMP_DIR}/{TEMP_FILE}"
    cmd = f"scrapy crawl WorkshopListing -a game_id={game_id} -o {abs_file}"
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    await proc.communicate()
    with open(abs_file, "r") as f:
        return sanic.response.json(json.loads(f.read()))


@app.route("/<game_id>/<item_id>")
async def dl(request, game_id, item_id):
    # if os.path.exists(TEMP_DIR):
    #    shutil.rmtree(TEMP_DIR)
    steam_user = os.environ["STEAM_USER"]
    steam_pass = os.environ["STEAM_PASSWORD"]
    cmd = f"steamcmd +login {steam_user} {steam_pass} +force_install_dir {TEMP_DIR} +workshop_download_item {game_id} {item_id} +quit"
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    # so this can error, but it will exit code 0 even if it errors.
    # an error is indicated by the absence of the expected output folder.
    dl_dir = f"{TEMP_DIR}/steamapps/workshop/content/{game_id}/{item_id}"
    if not os.path.exists(dl_dir):
        raise ServerError(stdout, status_code=403)

    # go to the folder and zip it up
    zip_path = f"{TEMP_DIR}/{game_id}-{item_id}.zip"
    zip_cmd = f"cd {dl_dir} && bsdtar -a -c -f {zip_path} *"
    proc2 = await asyncio.create_subprocess_shell(
        zip_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout2, stderr2 = await proc2.communicate()
    print(stdout2)
    if (os.path.exists(zip_path)):
        return await sanic.response.file(zip_path, filename=f"{item_id}.zip")
    else:
        raise ServerError(stdout2, status_code=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
