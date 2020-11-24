import os, time
from subprocess import Popen, PIPE
from os.path import basename
from zipfile import ZipFile
import pandas as pd


def make_dir(dirname):
    try:
        os.mkdir(dirname)
        print("Directory ", dirname, " Created ")
        return dirname
    except FileExistsError:
        pass


def path_find(name, *paths):
    for path in paths:
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)


def subprocess_cmd(command):
    print(command)
    try :
        process = Popen(command, stdout=PIPE, shell=True, universal_newlines=True)
        proc_stdout = process.communicate()[0].strip()
    except Exception as e:
        process = Popen(command, stdout=PIPE, shell=True, universal_newlines=False)
        proc_stdout = process.communicate()[0].strip()
    print(proc_stdout)


def packaging(filename, *bindings):
    zipname = r'dist\Objections.zip'
    with ZipFile(zipname, 'w') as zipObj:
        if os.path.exists(os.path.join('dist',filename)):
            zipObj.write(os.path.join('dist', filename), basename(filename))
        for binding in bindings:
            for folderName, subfolders, filenames in os.walk(binding):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    print(os.path.join(binding, basename(filePath)))
                    zipObj.write(filePath, os.path.join(basename(folderName), basename(filePath)))
        print(f'패키징을 완료하였습니다. {zipname}')


def install(lib):
    return f'pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install {lib}'


def force_reinstall(lib):
    return f'pip --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org install ' \
           f'"{lib}" --force-reinstall'


def venv_dir(foldername='venv'):
    return os.path.join(os.getcwd(), foldername)


def show_elapsed_time(function):
    def wrapper(*args, **kwargs):
        start = time.time()
        returns = function(*args, **kwargs)
        print(function.__name__, 'Elapsed {0:02d}:{1:02d}'.format(*divmod(int(time.time() - start), 60)))
        return returns
    return wrapper


def local_function_get_part_sys_3():
    with open('files/품목구분.xlsx', 'rb') as file:
        part_sys_3_df = pd.read_excel(file, converters={'품번': lambda x: str(x), '업체코드': lambda x: str(x)})
        part_sys_3_df = part_sys_3_df.sort_values(by=['우선순위'])
        return {k: part_sys_3_df['품목'].tolist()[n] for n, k in enumerate(part_sys_3_df['KEY'].tolist())}