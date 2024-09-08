import os
import time
import subprocess
from rich import print
from rich.markup import escape

import util
import config


# generate task for a single file
def generate_task(file: str) -> list[str]:
    newpath = util.convert_path(file)
    codec = "hevc_nvenc" if util.nvenc_support else "libx265"
    return [
        "ffmpeg",
        "-i",
        file,
        "-c:a",
        "aac",
        "-c:v",
        codec,
        "-b:v",
        "12M",
        "-maxrate",
        "20M",
        "-bufsize",
        "50M",
        newpath,
        "-y",
    ]


# ensures directory exists for media
def ensure_dirpath(file: str):
    newpath = util.convert_path(file)
    dirpath = os.path.dirname(newpath)
    if os.path.basename(dirpath) not in config.subdirs:
        print(f"making dir [yellow]{escape(dirpath)}[/yellow]")
        os.makedirs(dirpath, exist_ok=True)


# generate tasks from a list of files
def generate_tasks(target_files: list[str]) -> tuple[list[str], list[str]]:
    descrips = []
    cmds = []
    util.check_nvenc_support()
    for file in target_files:
        ensure_dirpath(file)
        newpath = util.convert_path(file)
        descrip = f"[yellow]encoding {file} to {newpath}[/yellow]"
        descrips.append(descrip)
        cmds.append(generate_task(file))

    return descrips, cmds


# execute tasks by group of 2
def execute_tasks(descrips: list[str], cmds: list[list[str]]):
    assert len(descrips) == len(cmds)

    current_processes = {}
    for i, (descrip, cmd) in enumerate(zip(descrips, cmds)):
        print(descrip)

        current_processes[i] = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        # block here to wait for the group of 2 to finish
        while len(current_processes) == 2 or (
            i == len(cmds) - 1 and len(current_processes) > 0
        ):
            for id, process in current_processes.items():
                if subprocess.Popen.poll(process) != None:
                    print(f"[green]finished {descrips[id]}[/green]")
                    del current_processes[id]
                    break
            time.sleep(1)
