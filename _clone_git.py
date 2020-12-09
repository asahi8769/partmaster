from utils.functions import subprocess_cmd
from datetime import datetime
from utils.config import *
from utils.functions import make_dir
import os

pull_dir = make_dir(f'clone_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
subprocess_cmd(f'git config --global user.name Ilhee Lee')
subprocess_cmd(f'git config --global user.email asahi8769@gmail.com')
subprocess_cmd(f'git clone --depth=1 {REPOSITORY[:-4]} {pull_dir}')

os.startfile(pull_dir)