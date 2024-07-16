import util
from rich import print


target_files, target_reasons = util.get_target_files()

print("The following files are queued for conversion:")
for file, reason in zip(target_files, target_reasons):
    print(f"{file} {reason}")

print("\n[[green]y[/green]]es/[[red]n[/red]]o to proceed/terminate: ", end="")
is_proceed = input() in ["y", "yes"]
if not is_proceed:
    quit()

descrips, cmds = util.generate_conversions(target_files)
util.exec_tasks(descrips, cmds)
