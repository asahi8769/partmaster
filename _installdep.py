from utils.functions import subprocess_cmd, install, force_reinstall
from utils.config import BASE_PYTHON, VENV_64_DIR, SCRIPTS_DIR


# subprocess_cmd(rf'cd {BASE_PYTHON} && python -m venv {VENV_64_DIR} && cd {SCRIPTS_DIR} && activate')
subprocess_cmd(f'cd {SCRIPTS_DIR} & {install("xlrd")}')
subprocess_cmd(f'cd {SCRIPTS_DIR} & {install("openpyxl")}')
subprocess_cmd(f'cd {SCRIPTS_DIR} & {install("matplotlib")}')
subprocess_cmd(f'cd {SCRIPTS_DIR} & {install("pyinstaller")}')
subprocess_cmd(f'cd {SCRIPTS_DIR} & {force_reinstall("pandas>=0.25.3,<0.26.0")}')
subprocess_cmd(f'cd {SCRIPTS_DIR} & {force_reinstall("numpy>=1.18.1,<1.19.0")}')

