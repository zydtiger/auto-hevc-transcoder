import os
import subprocess
from rich import print

import config

nvenc_support = False


# checks for nvenc support
def check_nvenc_support():
    global nvenc_support
    nvenc_support = "hevc_nvenc" in str(subprocess.check_output(["ffmpeg", "-codecs"]))
    nvenc_support_msg = "[green]True[/green]" if nvenc_support else "[red]False[/red]"
    print(f"support nvenc? {nvenc_support_msg}")


# checks if file is video
def is_file_video(path: str) -> bool:
    return path[-3:] in ["mp4", "mkv", "mov"]


# convert file path to be under `h265` and with extension `mp4`
def convert_path(path: str) -> str:
    path_parts = list(path.split(os.path.sep))
    path_parts[1] = config.hevc_name
    return os.path.join(*path_parts[:-1], path_parts[-1][:-3] + "mp4")
