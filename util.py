import os
import subprocess
from rich import print

import config

nvenc_support = False


# checks for nvenc support
def check_nvenc_support():
    global nvenc_support
    nvenc_support = "hevc_nvenc" in subprocess.check_output(
        ["ffmpeg", "-codecs"]
    ).decode("utf8")
    nvenc_support_msg = "[green]True[/green]" if nvenc_support else "[red]False[/red]"
    print(f"support nvenc? {nvenc_support_msg}")


# checks if file is video
def is_file_video(path: str) -> bool:
    return path[-3:] in ["mp4", "mkv", "mov"]


# convert file path to be under `h265` and with extension `mp4`
def convert_path(path: str) -> str:
    path = path.replace(config.source_name, config.hevc_name)
    return path[:-3] + "mp4"
