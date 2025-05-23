# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

# /// tarmac
# inputs:
#     pkg:
#         type: str
#         description: The name of the package to install
#         example: "git"
#     env:
#         type: dict
#         description: The environment variables to set
#         required: false
#         default: {}
#         example:
#             SOME_INSTALL_VAR: "value"
# ///

import os
import subprocess

from tarmac.operations import Failure, OperationInterface, run


def AptPkgInstalled(op: OperationInterface):
    pkg_name = op.inputs["pkg"]
    cmd = [
        "dpkg-query",
        "--showformat",
        "${Package}\t${db:Status-Status}\n",
        "-W",
        pkg_name,
    ]
    op.log(f"Checking if {pkg_name} is installed")
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode == 1:
        # No package found
        pass
    elif p.returncode == 0:
        for line in p.stdout.splitlines():
            package, status = line.split("\t")
            if package != pkg_name:
                continue
            if status == "installed":
                op.log(f"{pkg_name} is already installed")
                op.changed(False)
                return
    else:
        raise subprocess.CalledProcessError(p.returncode, cmd, p.stdout, p.stderr)
    op.log(f"{pkg_name} is not installed")
    cmd = [
        "apt-get",
        "-q",  # quiet
        "-y",  # assume yes
        "-o",
        "DPkg::Options::=--force-confold",  # keep old config files
        "-o",
        "DPkg::Options::=--force-confdef",  # keep new config files
        "install",  # install package
        pkg_name,  # package name
    ]
    env = os.environ.copy()
    env["DEBIAN_FRONTEND"] = "noninteractive"  # don't ask questions
    env["APT_LISTCHANGES_FRONTEND"] = "none"  # don't show changelogs
    env["APT_LISTBUGS_FRONTEND"] = "none"  # don't show bug reports
    env["UCF_FORCE_CONFFOLD"] = "1"  # keep old config files
    env.update(op.inputs["env"] or {})
    op.log(f"Installing {pkg_name}")
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    op.log(p.stdout)
    if "Setting up" in p.stdout:
        op.changed()
    if p.returncode != 0:
        raise Failure(f"Failed to install {pkg_name}: {p.stderr}")


run(AptPkgInstalled)
