import os
import sys

from cltoolbox.cltoolbox import Program

main = Program()
command = main.command
arg = main.arg
parse = main.parse
execute = main.execute

# add git submodule to path to allow imports to work
submodule_names = ["cltoolbox/docutils/docutils", "cltoolbox/python-rst2ansi"]
for submodule_name in submodule_names:
    (parent_folder_path, current_dir) = os.path.split(os.path.dirname(__file__))
    sys.path.append(os.path.join(parent_folder_path, submodule_name))
