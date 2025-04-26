# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests>=2",
# ]
# ///

# /// tarmac
# description: Download a release asset from a Gitea repository
# inputs:
#     gitea_url:
#         type: str
#         description: URL of the Gitea instance
#         example: "https://git.mycompany.com"
#         required: true
#     repo:
#         type: str
#         description: Gitea repository to download from
#         example: "org/repo"
#         required: true
#     asset:
#         type: str
#         description: Name of the asset to download
#         example: "my_binary"
#         required: true
#     version:
#         type: str
#         description: Version of the release to download, or "latest" to get the latest release
#         default: "latest"
#         example: "1.2.3"
#     auth_token:
#         type: str
#         description: Gitea API token for authentication
#         required: true
#     path:
#         type: str
#         description: Path to save the downloaded asset
#         example: "/usr/local/bin/my_binary"
#         required: true
#     version_file:
#         type: str
#         description: Path to save the version file
#         example: "/usr/local/bin/my_binary.version"
#         required: true
#     backup:
#         type: bool
#         description: Whether to backup the existing asset to {path}.old
#         default: true
# outputs:
#     version:
#         type: str
#         description: Version of the release that was downloaded
#         example: "1.2.3"
# ///

import os

import requests

from tarmac.operations import OperationInterface, run


def gitea_release_asset_installed(op: OperationInterface):
    version = op.inputs["version"]
    auth_token = op.inputs["auth_token"]
    gitea_url = op.inputs["gitea_url"]
    repo = op.inputs["repo"]
    asset = op.inputs["asset"]
    path = op.inputs["path"]
    version_file = op.inputs["version_file"]
    backup = op.inputs["backup"]
    if version == "latest":
        op.log("Fetching latest version from Gitea")
        with requests.get(
            f"{gitea_url}/api/v1/repos/{repo}/releases/latest",
            headers={"Authorization": "token " + auth_token},
        ) as response:
            response.raise_for_status()
            version = response.json()["tag_name"]
    op.log(f"Using version {version}")
    op.outputs["version"] = version
    if os.path.isfile(path):
        if os.path.isfile(version_file):
            if open(version_file).read() == version:
                op.log(f"Version {version} already installed")
                op.changed(False)
                return
        else:
            op.log(f"Version file {version_file} does not exist.")
    else:
        op.log(f"File {path} does not exist.")

    op.log(f"Downloading version {version} from Gitea")
    if backup:
        backup_path = path + ".old"
        if os.path.exists(backup_path):
            op.log(f"Removing old backup {backup_path}")
            os.unlink(backup_path)
        if os.path.exists(path):
            op.log(f"Backing up {path} to {backup_path}")
            os.rename(path, backup_path)
    asset_url = f"{gitea_url}/{repo}/releases/download/{version}/{asset}"
    op.log(f"Downloading {asset_url} to {path}")
    with requests.get(
        asset_url,
        headers={"Authorization": "token " + auth_token},
        stream=True,
    ) as response:
        response.raise_for_status()
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    op.log(f"Saving version to {version_file}")
    with open(version_file, "w") as f:
        f.write(version)
    op.log(f"Version {version} downloaded and saved to {path}")
    op.changed(True)
    return


run(gitea_release_asset_installed)
