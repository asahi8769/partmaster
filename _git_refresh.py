from utils.functions import subprocess_cmd
from datetime import datetime
from utils.config import *

subprocess_cmd(f'git config --global user.name Ilhee Lee')
subprocess_cmd(f'git config --global user.email asahi8769@gmail.com')
subprocess_cmd(f'git init')
subprocess_cmd(f'git rm -rf --cached .')
subprocess_cmd(f'git add .')
subprocess_cmd(f'git config --global http.sslVerify false')
subprocess_cmd(f'git commit -m "{datetime.now().strftime("%Y%m%d_%H")}"')
subprocess_cmd(f'git remote add origin {REPOSITORY}')
subprocess_cmd(f'git push --force origin master')
subprocess_cmd(f'git remote remove origin')