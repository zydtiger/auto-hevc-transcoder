import os
import time
import platform
import subprocess
from rich import print


# checks if file is video
def is_file_video(path: str) -> bool:
    return path[-3:] in ["mp4", "mkv", "mov"]


# get all files under a dir path recursively
def get_all_video_files(path: str) -> list[str]:
    entries = os.listdir(path)
    full_entries = [os.path.join(path, entry) for entry in entries]
    files = [
        # recursively reads entry path if it is a dir
        get_all_video_files(full_entry) if os.path.isdir(full_entry) else [full_entry]
        for full_entry in full_entries
    ]
    flat_files = sum(files, [])
    return list(filter(lambda file: is_file_video(file), flat_files))


# get the duration of a video file to verify it's the same file
def get_duration(file: str) -> float:
    info_str = subprocess.check_output(
        [
            "ffprobe",
            file,
            "-hide_banner",
            "-show_entries",
            "format=duration",
            "-v",
            "quiet",
        ]
    ).decode("ascii")
    start_index = info_str.find("=") + 1
    end_index = info_str.find(os.linesep, start_index)
    return float(info_str[start_index:end_index])


# convert file path to be under `h265` and with extension `mp4`
def convert_path(path: str) -> str:
    path_parts = list(path.split(os.path.sep))
    path_parts[1] = "h265"
    return os.path.join(*path_parts[:-1], path_parts[-1][:-3] + "mp4")


# gets target files from `source` dir by checking if the same video files is already present in `h265`
def get_target_files() -> tuple[list[str], list[str]]:
    src_files = get_all_video_files(os.path.join("..", "source"))
    dest_files = get_all_video_files(os.path.join("..", "h265"))

    target_reasons = []
    target_files = []
    for file in src_files:
        is_target_exist = convert_path(file) in dest_files
        is_target_corrupt = False

        if is_target_exist:
            try:
                src_len = get_duration(file)
                dest_len = get_duration(convert_path(file))
                is_target_corrupt = abs(src_len - dest_len) > 1
            except:
                is_target_corrupt = True

        if not is_target_exist:
            target_reasons.append("[cyan]Does Not Exist[/cyan]")
            target_files.append(file)

        if is_target_corrupt:
            target_reasons.append("[red]Corrupted[/red]")
            target_files.append(file)

    return target_files, target_reasons


def generate_conversions(target_files: list[str]) -> tuple[list[str], list[str]]:
    descrips = []
    cmds = []
    for file in target_files:
        newpath = convert_path(file)

        # create dir if needed
        path_parts = list(newpath.split(os.path.sep))
        dirpath = os.path.join(*path_parts[:-1])
        if len(path_parts) > 3:
            print(f"[cyan]making dir: {dirpath}[/cyan]")
            os.makedirs(dirpath, exist_ok=True)

        descrip = f"[yellow]encoding {file} to {newpath}[/yellow]"
        descrips.append(descrip)

        codec = "hevc_nvenc" if platform.system() == "Windows" else "libx265"
        cmds.append(
            [
                "ffmpeg",
                "-i",
                file,
                "-c:a",
                "aac",
                "-c:v",
                codec,
                "-preset",
                "slow",
                newpath,
                "-y",
            ]
        )

    return descrips, cmds


# execute tasks by group of 2
def exec_tasks(descrips: list[str], cmds: list[list[str]]):
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
