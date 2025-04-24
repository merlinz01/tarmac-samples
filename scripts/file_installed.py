# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests>=2",
# ]
# ///

# /// tarmac
# description: Check if a file is installed and install it if not.
# inputs:
#     source:
#         type: str
#         description: The source of the file to install
#         example:
#             - "/path/to/file.txt"
#             - "https://example.com/file.txt"
#     source_type:
#         type: str
#         description: The type of source
#         example:
#             - local  # Copy from local file (default)
#             - http  # Download from HTTP(S) URL
#             - source  # Copy from literal string provided in the source parameter
#         default: "local"
#         required: false
#     path:
#         type: str
#         description: The path to install the file to
#         example: "/path/to/file.txt"
#     overwrite:
#         type: bool
#         description: Whether to overwrite the file if it already exists and is different
#         default: true
#         required: false
# ///

import io
import os
from typing import BinaryIO

from tarmac.operations import OperationInterface, run


def install_from_stream(source: BinaryIO, path: str) -> bool:
    chunk_size = 8192
    pos = 0
    changed = False
    try:
        f = open(path, "r+b")
    except FileNotFoundError:
        f = open(path, "w+b")
    with f:
        while True:
            chunk = source.read(chunk_size)
            if not chunk:
                break
            f.seek(pos)
            if f.read(len(chunk)) != chunk:
                f.seek(pos)
                f.write(chunk)
                changed = True
            pos += len(chunk)
        f.seek(0, os.SEEK_END)
        if f.tell() > pos:
            changed = True
        f.truncate(pos)
    return changed


def FileInstalled(op: OperationInterface):
    source: str = op.inputs["source"]
    source_type: str = op.inputs["source_type"]
    path: str = op.inputs["path"]
    overwrite: bool = op.inputs["overwrite"]
    if os.path.isfile(path) and not overwrite:
        op.log(f"{path} already exists. Not overwriting.")
        op.changed(False)
        return
    if os.path.exists(path) and not os.path.isfile(path):
        op.log(f"{path} exists but is not a file. Removing.")
        os.remove(path)
    op.log(f"Installing {path}")
    if source_type == "local":
        op.log(f"Copying from {source}")
        with open(source, "rb") as src_file:
            changed = install_from_stream(src_file, path)
    elif source_type == "http":
        op.log(f"Downloading from {source}")
        import requests

        response = requests.get(source, stream=True)
        response.raise_for_status()
        assert response.raw is not None, "Response raw stream is None"
        changed = install_from_stream(response.raw, path)  # type: ignore
    elif source_type == "source":
        op.log("Installing from source string")
        source_io = io.BytesIO(source.encode())
        changed = install_from_stream(source_io, path)
    else:
        raise ValueError(f"Unknown source type: {source_type}")
    if not changed:
        op.log(f"{path} is already installed")
        op.changed(False)
    else:
        op.log(f"{path} installed successfully")
        op.changed(True)


run(FileInstalled)
