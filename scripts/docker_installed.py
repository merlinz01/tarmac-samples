# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
# ]
# ///

# /// tarmac
# description: Install Docker on a Linux system
# ///
import os
import subprocess
import sys

import requests

from tarmac.operations import Failure, OperationInterface, run


def docker_installed(op: OperationInterface):
    if sys.platform != "linux":
        raise Failure("docker_installed is only supported on Linux")
    distro = None
    distro_version = None
    for line in open("/etc/os-release"):
        if line.startswith("VERSION_CODENAME="):
            distro_version = line[17:].strip()
        if line.startswith("ID="):
            distro = line[3:].strip()
    if distro is None:
        raise Failure("Could not find VERSION_CODENAME in /etc/os-release")
    if distro not in ("ubuntu", "debian"):
        raise Failure("Unsupported platform for docker_installed: " + repr(distro))
    if distro_version is None:
        raise Failure("Could not find ID in /etc/os-release")
    if os.path.isfile("/usr/bin/docker"):
        op.log("Docker is already installed.")
        op.changed(False)
        return
    op.log("Docker is not installed.")
    if not os.path.isdir("/etc/apt/keyrings"):
        op.log("Creating /etc/apt/keyrings directory.")
        os.mkdir("/etc/apt/keyrings")
    if not os.path.isfile("/etc/apt/keyrings/docker.asc"):
        op.log("Downloading Docker GPG key.")
        url = f"https://download.docker.com/linux/{distro}/gpg"
        with requests.get(url, allow_redirects=True) as response:
            response.raise_for_status()
            gpgkey = response.content.decode("utf-8")
        with open("/etc/apt/keyrings/docker.asc", "w") as keyring:
            keyring.write(gpgkey)
        os.chmod("/etc/apt/keyrings/docker.asc", 0o644)
    if not os.path.isfile("/etc/apt/sources.list.d/docker.list"):
        op.log("Adding Docker repository to apt sources.")
        arch = subprocess.getoutput("dpkg --print-architecture")
        with open("/etc/apt/sources.list.d/docker.list", "w") as repo:
            repo.write(
                f"deb [arch={arch} signed-by=/etc/apt/keyrings/docker.asc] "
                f"https://download.docker.com/linux/{distro} {distro_version} stable"
            )
        os.chmod("/etc/apt/sources.list.d/docker.list", 0o644)
    op.log("Updating apt package list.")
    subprocess.run(["apt-get", "update"], check=True)
    op.log("Installing Docker.")
    cmd = [
        "apt-get",
        "install",
        "-y",
        "docker-ce",
        "docker-ce-cli",
        "containerd.io",
        "docker-buildx-plugin",
        "docker-compose-plugin",
    ]
    env = os.environ.copy()
    env["DEBIAN_FRONTEND"] = "noninteractive"
    env["APT_LISTCHANGES_FRONTEND"] = "none"
    p = subprocess.run(cmd, text=True, capture_output=True, env=env)
    if p.returncode != 0:
        raise Failure(f"Failed to install docker packages: {p.stderr}")
    op.log("Docker installed successfully.")
    op.changed(True)
    return


run(docker_installed)
