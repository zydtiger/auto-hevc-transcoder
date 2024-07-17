import sys
import preprocessing
import execution
from rich import print
from rich.markup import escape

target_files, target_reasons = preprocessing.get_target_files()

print("\n\nThe following files are queued for conversion:")
for file, reason in zip(target_files, target_reasons):
    print(f"{escape(file)} {reason}")

print("\n[[green]y[/green]]es/[[red]n[/red]]o to proceed/terminate: ", end="")
is_proceed = input() in ["y", "yes"] or "-y" in sys.argv
if not is_proceed:
    quit()

descrips, cmds = execution.generate_tasks(target_files)
execution.execute_tasks(descrips, cmds)
