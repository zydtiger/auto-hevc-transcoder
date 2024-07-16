import os
import subprocess
from rich import print

import util
import config


# get all files under a dir path recursively
def get_all_video_files(path: str) -> list[str]:
    print(f"getting all video files from [yellow]{path}[/yellow]")
    entries = os.listdir(path)
    full_entries = [os.path.join(path, entry) for entry in entries]
    files = [
        # recursively reads entry path if it is a dir
        get_all_video_files(full_entry) if os.path.isdir(full_entry) else [full_entry]
        for full_entry in full_entries
    ]
    flat_files = sum(files, [])
    return list(filter(lambda file: util.is_file_video(file), flat_files))


# get the duration of a video file to verify it's the same file
def get_duration(file: str) -> float:
    print(f"getting video file duration at [yellow]{file}[/yellow]")
    info_str = str(
        subprocess.check_output(
            [
                "ffprobe",
                file,
                "-hide_banner",
                "-show_entries",
                "format=duration",
                "-v",
                "quiet",
            ]
        )
    )
    start_index = info_str.find("=") + 1
    end_index = info_str.find(os.linesep, start_index)
    return float(info_str[start_index:end_index])


# gets target files from source dir by checking if the same video files is already present in hevc dir
def get_target_files() -> tuple[list[str], list[str]]:
    src_files = get_all_video_files(os.path.join(config.media_dir, config.source_name))
    dest_files = get_all_video_files(os.path.join(config.media_dir, config.hevc_name))

    target_reasons = []
    target_files = []
    for file in src_files:
        newpath = util.convert_path(file)
        is_target_exist = newpath in dest_files
        is_target_corrupt = False

        if is_target_exist:
            try:
                src_len = get_duration(file)
                dest_len = get_duration(newpath)
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
