# /// tarmac
# description: Change Unix file ownership
# inputs:
#     path:
#         type: str
#         description: The path to change permissions on
#         example: "/path/to/file.txt"
#     user:
#         type: str
#         description: The user to set as the owner
#         example: "username"
#     group:
#         type: str
#         description: The group to set as the owner
#         example: "groupname"

import grp
import os
import pwd

from tarmac.operations import Failure, OperationInterface, run


def Chmod(op: OperationInterface):
    path = op.inputs["path"]
    user = op.inputs["user"]
    group = op.inputs["group"]
    uid = pwd.getpwnam(user).pw_uid
    gid = grp.getgrnam(group).gr_gid

    try:
        stat = os.stat(path)
    except FileNotFoundError as e:
        raise Failure(f"{path} does not exist") from e
    except PermissionError as e:
        raise Failure(f"Permission denied to access {path}") from e

    if stat.st_uid == uid and stat.st_gid == gid:
        op.log(f"Ownership of {path} is already set to {user}:{group}")
        op.changed(False)
        return

    os.chown(path, uid, gid)
    op.log(f"Changed owner of {path} from {stat.st_uid}:{stat.st_gid} to {uid}:{gid}")


run(Chmod)
