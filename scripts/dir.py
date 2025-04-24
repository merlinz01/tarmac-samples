# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

# /// tarmac
# description: Create a directory
# inputs:
#     path:
#         type: str
#         description: The path to the directory to create
#         example: /path/to/directory
#     parents:
#         type: bool
#         description: Create parent directories if they do not exist
#         default: false
# ///

import os

from tarmac.operations import Failure, OperationInterface, run


def Dir(op: OperationInterface):
    path = op.inputs["path"]
    parents = op.inputs["parents"]
    if os.path.exists(path):
        op.log(f"Directory {path} already exists.")
        op.changed(False)
        return
    try:
        if parents:
            os.makedirs(path)
        else:
            os.mkdir(path)
    except OSError as e:
        raise Failure(f"Error creating directory {path}: {e}")
    op.log(f"Directory {path} created successfully.")
    op.changed(True)


run(Dir)
