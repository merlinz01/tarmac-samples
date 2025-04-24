# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///


# /// tarmac
# description: Ensure a systemd service is running
# inputs:
#     service:
#         type: str
#         description: The name of the systemd service to check
#         example: "nginx"
# ///

import subprocess

from tarmac.operations import Failure, OperationInterface, run


def SystemdServiceRunning(op: OperationInterface):
    service = op.inputs["service"]
    p = subprocess.run(
        ["systemctl", "is-active", service],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if p.returncode == 0:
        op.log(f"Service {service} is already running.")
        op.changed(False)
        return
    elif p.returncode == 4:
        op.log(f"Service {service} is not running.")
    else:
        raise Failure(f"Error checking service status: {p.stderr}")

    p = subprocess.run(["systemctl", "start", service], capture_output=True, text=True)
    op.log(p.stdout)
    if p.returncode == 5:
        raise Failure(f"Service {service} not found.")
    elif p.returncode != 0:
        raise Failure(f"Error starting service {service}: {p.stderr}")
    op.log(f"Service {service} started successfully.")
    op.changed(True)


run(SystemdServiceRunning)
