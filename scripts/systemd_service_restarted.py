# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///


# /// tarmac
# description: Restart a systemd service
# inputs:
#     service:
#         type: str
#         description: The name of the systemd service to restart
#         example: "nginx"
# ///

import subprocess

from tarmac.operations import Failure, OperationInterface, run


def SystemdServiceRestarted(op: OperationInterface):
    service = op.inputs["service"]
    p = subprocess.run(
        ["systemctl", "restart", service], capture_output=True, text=True
    )
    op.log(p.stdout)
    if p.returncode == 5:
        raise Failure(f"Service {service} not found.")
    elif p.returncode != 0:
        raise Failure(f"Error starting service {service}: {p.stderr}")
    op.log(f"Service {service} restarted successfully.")
    op.changed(True)


run(SystemdServiceRestarted)
