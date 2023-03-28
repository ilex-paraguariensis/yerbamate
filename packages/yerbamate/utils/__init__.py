from rich.padding import Padding
from rich.console import Console
from rich.markdown import Markdown
from glob import glob
import os
import shutil
import ipdb

# remove_indent = lambda text: "\n".join(
#     [line[len(line) - len(line.lstrip()) :] for line in text.split("\n")]
# )
def remove_indent(text: str):
    indents: dict[int, int] = {}
    for line in [l for l in text.splitlines() if l.strip() != ""]:
        indent = len(line) - len(line.lstrip())
        if indent not in indents:
            indents[indent] = 0
        indents[indent] += 1

    selected_indent = max(indents.items(), key=lambda x: x[1])[0]
    def indent_remover(line: str):
        current_indent = len(line) - len(line.lstrip())
        indent = min(current_indent, selected_indent)
        return line[indent:]

    return "\n".join([indent_remover(line) for line in text.split("\n")])


console = Console(width=75)
print = console.print
def print_markdown(x, svg:bool=False, file_name:str="", title:str=""):
    if svg:
        console = Console(width=50, record=True)
        local_print = console.print
    else:
        local_print = print
    local_print(Padding(Markdown(remove_indent(x)), (1, 0, 0, 5)))
    if svg:
        console.save_svg(file_name, title=title)
        


def rmwithin(path: str):
    for file in glob(path + "*"):
        if os.path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)
