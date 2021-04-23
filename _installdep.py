from utils.functions import subprocess_cmd, install, force_reinstall
from utils.config import SCRIPTS_DIR
import os


subprocess_cmd(rf'cd {SCRIPTS_DIR} && python -m venv {SCRIPTS_DIR} && activate')
# subprocess_cmd(f'{install("xlrd")}')
# subprocess_cmd(f'{install("openpyxl")}')
# subprocess_cmd(f'{install("matplotlib")}')
# subprocess_cmd(f'{install("pyinstaller")}')
# subprocess_cmd(f'{force_reinstall("pandas>=0.25.3,<0.26.0")}')

# subprocess_cmd(f'{force_reinstall("torch==1.5.1+cpu torchvision==0.6.1+cpu -f https://download.pytorch.org/whl/torch_stable.html")}')
# subprocess_cmd(f'{install(os.path.join(os.getcwd(),"files","wheels", r"torch-1.5.0+cpu-cp37-cp37m-win_amd64.whl"))}')
# subprocess_cmd(f'{install("torchtext")}')
# subprocess_cmd(f'{install("-U spacy")}')
# subprocess_cmd(f'python -m spacy download en')
# subprocess_cmd(f'{force_reinstall("numpy>=1.18.1,<1.19.0")}')
# subprocess_cmd(f'{install("bs4")}')
# subprocess_cmd(f'{install("request")}')
# subprocess_cmd(f'{install("lxml")}')
# subprocess_cmd(f'{install("html5lib")}')
subprocess_cmd(f'{install("selenium")}')
subprocess_cmd(f'{install("zipfile36")}')
# subprocess_cmd(f'{install("chromedriver-autoinstaller")}')
