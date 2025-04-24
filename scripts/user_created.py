# /// tarmac
# description: Ensure a user exists
# inputs:
#     name:
#         type: str
#         description: The name of the user to create
#         example: bob
#     system:
#         type: bool
#         description: Whether to create a system user
#         default: false
# ///

import pwd
import subprocess

from tarmac.operations import Failure, OperationInterface, run


def UserCreated(op: OperationInterface):
    user = op.inputs["user"]
    system = op.inputs["system"]
    try:
        pwd.getpwnam(user)
        op.log(f"User {user} already exists.")
        return
    except KeyError:
        op.log(f"User {user} does not exist.")
    except PermissionError as e:
        raise Failure(f"Permission denied to access user {user}") from e
    cmd = ["adduser", user]
    if system:
        cmd.append("--system")
    p = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    op.log(p.stdout)
    if p.returncode != 0:
        raise Failure(f"Error creating user {user}: {p.stderr}")
    op.log(f"User {user} created successfully.")
    op.changed(True)


run(UserCreated)
