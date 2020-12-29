import os, time
from subprocess import Popen, PIPE
from os.path import basename
from zipfile import ZipFile
from functools import reduce
import requests
from lxml import html
from io import BytesIO


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


def try_until_success(function):
    def wrapper(*args, **kwargs):
        while True:
            try:
                returns = function(*args, **kwargs)
            except Exception as e:
                print(f"{function.__name__} failed. Trying Again...")
            else :
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


def update_chromedriver(browserVersion=None):

    # proxies = {"http": "http://85.237.57.198:44959",
    #            "https" : "http://116.0.2.94:43379"}


    if browserVersion is None:
        browserVersion = input("Type your current chrome version(ex.87) :")
    url_versions = "https://chromedriver.chromium.org/downloads"
    response = requests.get(url_versions, verify=False)
    webpage = html.fromstring(response.content)
    links = [i for i in webpage.xpath('//a/@href') if
             "https://chromedriver.storage.googleapis.com/index.html?path=" + str(browserVersion) in i]
    version = links[0].split("=")[1][:-1]
    print(f"Downloading Chromedriver version {version}")
    url = "https://chromedriver.storage.googleapis.com/"+version+"/chromedriver_win32.zip"
    response = requests.get(url, verify=False)
    print(response.status_code)
    with ZipFile(BytesIO(response.content), 'r') as zipObj:
        zipObj.extract("chromedriver.exe", path="driver", pwd=None)
    print("Chromedriver is successfully replaced")

# if __name__ == "__main__":
#     update_chromedriver(browserVersion=83)