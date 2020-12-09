from utils.functions import subprocess_cmd, install, force_reinstall
from utils.config import SCRIPTS_DIR


subprocess_cmd(rf'python -m venv {SCRIPTS_DIR} && activate')
subprocess_cmd(f'{install("xlrd")}')
subprocess_cmd(f'{install("openpyxl")}')
subprocess_cmd(f'{install("matplotlib")}')
subprocess_cmd(f'{install("pyinstaller")}')
subprocess_cmd(f'{force_reinstall("pandas>=0.25.3,<0.26.0")}')
subprocess_cmd(f'{force_reinstall("numpy>=1.18.1,<1.19.0")}')
