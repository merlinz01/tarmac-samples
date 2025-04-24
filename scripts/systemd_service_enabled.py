# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///


# /// tarmac
# description: Enable a systemd service
# inputs:
#     service:
#         type: str
#         description: The name of the systemd service to enable
#         example: "nginx"
# ///

import subprocess

from tarmac.operations import Failure, OperationInterface, run


def SystemdServiceEnabled(op: OperationInterface):
    service = op.inputs["service"]
    p = subprocess.run(
        ["systemctl", "is-enabled", service],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if p.returncode == 0:
        op.log(f"Service {service} is already enabled.")
        op.changed(False)
        return
    elif p.returncode == 1:
        op.log(f"Service {service} is not enabled.")
    elif p.returncode == 4:
        raise Failure(f"Service {service} not found.")
    else:
        raise Failure(f"Error checking service status: {p.stderr}")

    p = subprocess.run(["systemctl", "enable", service], capture_output=True, text=True)
    if p.returncode != 0:
        raise Failure(f"Error enabling service {service}: {p.stderr}")
    op.log(p.stdout)
    op.log(f"Service {service} enabled successfully.")
    op.changed(True)


run(SystemdServiceEnabled)
