"""Upload the generated audio folders to Cloudflare R2 with rclone.

Usage:
    python tools/upload_audio.py --dry-run   # list what would be uploaded
    python tools/upload_audio.py             # upload (only new/changed files)

Put R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY and R2_ACCOUNT_ID in the
git-ignored .env file at the repo root (or set them as environment variables).

Keys are handed to rclone through environment variables, so no config file
holding secrets is created. Local files in ../audio/ are never deleted, and
the remote is never pruned (rclone copy, not sync).
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

BUCKET = "vedanta-audio"
AUDIO = Path(__file__).resolve().parents[2] / "audio"
NAMES = ("R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_ACCOUNT_ID")


def read_env_file():
    path = Path(__file__).resolve().parents[1] / ".env"
    values = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip().strip('"').strip("'")
    return values


ENV_FILE = read_env_file()


def get_var(name):
    value = ENV_FILE.get(name) or os.environ.get(name)
    if value or sys.platform != "win32":
        return value
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return winreg.QueryValueEx(k, name)[0]
    except OSError:
        return None


def find_rclone():
    exe = shutil.which("rclone")
    if exe:
        return exe
    base = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet"
    for pattern in ("Links/rclone.exe", "Packages/Rclone.Rclone*/**/rclone.exe"):
        for hit in base.glob(pattern):
            return str(hit)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--prune", action="store_true",
                        help="also delete bucket MP3s that no longer exist locally")
    args = parser.parse_args()

    values = {n: get_var(n) for n in NAMES}
    missing = [n for n, v in values.items() if not v]
    if missing:
        sys.exit("Missing variables: " + ", ".join(missing))

    rclone = find_rclone()
    if not rclone:
        sys.exit("rclone not found. Restart Zed after installing it.")
    if not AUDIO.is_dir():
        sys.exit(f"No audio folder at {AUDIO}")

    env = dict(os.environ)
    env.update(
        RCLONE_CONFIG_R2_TYPE="s3",
        RCLONE_CONFIG_R2_PROVIDER="Cloudflare",
        RCLONE_CONFIG_R2_ACCESS_KEY_ID=values["R2_ACCESS_KEY_ID"],
        RCLONE_CONFIG_R2_SECRET_ACCESS_KEY=values["R2_SECRET_ACCESS_KEY"],
        RCLONE_CONFIG_R2_ENDPOINT=f"https://{values['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        RCLONE_CONFIG_R2_ACL="private",
        RCLONE_CONFIG_R2_NO_CHECK_BUCKET="true",
    )
    cmd = [rclone, "sync" if args.prune else "copy", str(AUDIO), f"R2:{BUCKET}",
           "--include", "*.mp3", "--include", "*.xml", "--include", "*.jpg",
           "--progress", "--transfers", "4"]
    if args.dry_run:
        cmd.append("--dry-run")
    sys.exit(subprocess.run(cmd, env=env).returncode)


if __name__ == "__main__":
    main()
