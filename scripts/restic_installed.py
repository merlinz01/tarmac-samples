# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
# ]
# ///

# /// tarmac
# description: Install the restic backup tool
# ///
import bz2
import os

import requests

from tarmac.operations import OperationInterface, run


def install_restic(op: OperationInterface):
    if os.path.exists("/usr/local/bin/restic"):
        op.log("Restic is already installed.")
        op.changed(False)
        return
    op.log("Installing restic from GitHub.")
    with requests.get(
        "https://api.github.com/repos/restic/restic/releases/latest"
    ) as response:
        version = response.json()["tag_name"][1:]
    asset_url = f"https://github.com/restic/restic/releases/download/v{version}/restic_{version}_linux_amd64.bz2"
    op.log(f"Downloading version {version}.")
    with requests.get(asset_url, stream=True) as response:
        response.raise_for_status()
        with open("/usr/local/bin/restic", "wb") as f:
            decompressor = bz2.BZ2Decompressor()
            for chunk in response:
                chunk = decompressor.decompress(chunk)
                f.write(chunk)
    op.log("Making restic executable.")
    os.chmod("/usr/local/bin/restic", 0o750)
    op.log("Restic installed successfully.")
    op.changed(True)
    return


run(install_restic)
