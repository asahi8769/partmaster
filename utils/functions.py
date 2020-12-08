import os, time
from subprocess import Popen, PIPE
from os.path import basename
from zipfile import ZipFile
from functools import reduce


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


def flatten(ls):
    """
    ls : list
    flattens multi-dimensional list
    """
    return list(set([i for i in reduce(lambda x, y: x + y, ls)]))


def remove_duplication(ls):
    """
    ls : list
    remove duplicated items while maintaining order
    """
    seen = set()
    seen_add = seen.add
    return [i for i in ls if not (i in seen or seen_add(i))]