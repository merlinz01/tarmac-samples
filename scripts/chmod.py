# /// tarmac
# description: Change Unix file permissions
# inputs:
#     path:
#         type: str
#         description: The path to change permissions on
#         example: "/path/to/file.txt"
#     mode:
#         type: int
#         description: The mode to set on the file
#         example: 0o644

import os

from tarmac.operations import Failure, OperationInterface, run


def Chmod(op: OperationInterface):
    path = op.inputs["path"]
    mode = op.inputs["mode"]
    if not 0 <= mode <= 0o777:
        raise Failure(f"Invalid mode {oct(mode)}. Must be between 0o000 and 0o777.")

    try:
        stat = os.stat(path)
    except FileNotFoundError as e:
        raise Failure(f"{path} does not exist") from e
    except PermissionError as e:
        raise Failure(f"Permission denied to access {path}") from e

    if stat.st_mode & 0o777 == mode:
        op.log(f"Permissions of {path} are already set to {oct(mode)}")
        op.changed(False)
        return

    os.chmod(path, mode)
    op.log(
        f"Changed permissions of {path} from {oct(stat.st_mode & 0o777)} to {oct(mode)}"
    )


run(Chmod)
