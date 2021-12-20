import dataclasses
import os
import pathlib
from abc import ABC
from dataclasses import dataclass
from typing import Optional, List

import yaml

from django_cli.config import DBEngine, INSTALLED_APP, MIDDLEWARE, EXTRA
from django_cli.const import FILE_EXIST_ERROR, DEFAULT_REQUIREMENT_FILE
from django_cli.utils import create_secret_key, log, execute, pip_name, error

PATH = pathlib.Path(__file__).resolve().parent.parent

SETUP_CONFIG_FILE = "setup.yaml"
ENV_FILE = ".env"
STATIC_FILE_SETTINGS = """STATICFILES_DIRS = [BASE_DIR / 'static',]"""
MEDIA_FILE_SETTINGS = """MEDIA_ROOT = BASE_DIR / 'media'"""
TEMPLATE_SETTINGS = """BASE_DIR / "template\""""


def safe_create_dir(func):
    """A decorator that enables to run function that has directory creation responsibility, without throwing
    errors """

    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except FileExistsError:
            error(FILE_EXIST_ERROR)

    return wrapper


@dataclass
class DataClassAbstract(ABC):

    def __init__(self, **kwargs):
        names = set([f.name for f in dataclasses.fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)
        self.__post_init__()

    def get_dict(self) -> dict:
        """
        Returns Non nil fields
        :return: dict
        """
        _dict = {}
        for key in self.__dict__:
            if issubclass(type(self.__dict__[key]), DataClassAbstract):
                _dict[key] = self.__dict__[key].get_dict()

            else:
                _dict[key] = self.__dict__[key]
        return _dict

    def dump_upper(self) -> dict:
        """
        Returns Dictionary with uppercase keys
        :return:
        """
        return {k.upper(): v for k, v in self.get_dict().items() if v}

    def __post_init__(self):
        for val in self.__dict__:
            if type(self.__dict__[val]) is str and self.__dict__[val].startswith("$"):
                self.__dict__[val] = os.environ.get(self.__dict__[val][1:])

        env = self.__dict__.get("env")
        if env:
            for data in env:
                if env[data].startswith("$"):
                    self.__dict__["env"][data] = os.environ.get(env[data][1:], "")


@dataclass(init=False)
class DBConfig(DataClassAbstract):
    """
    Database Config
    """
    engine: str
    name: str = ""
    user: str = ""
    password: str = ""
    host: str = ""
    port: str = ""
    option: Optional[dict] = None


@dataclass(init=False)
class CacheConfig(DataClassAbstract):
    """
    Cache Config
    """
    backend: str = ""
    location: str = ""


DefaultDBConfig = DBConfig(engine=DBEngine["sqlite3"], name="db.sqlite3")


@dataclass(init=False)
class SetupProjectState(DataClassAbstract):
    """
    Setup Project State
    """
    name: str
    libraries: List[str] = None
    required: List[str] = None
    database: Optional[DBConfig] = None
    cache: Optional[CacheConfig] = None
    env: dict = None
    # docker: bool = False
    requirements: bool = False
    template: bool = True
    static: bool = True
    media_files: bool = True

    ENV_SECRET = ["database", "env", "cache"]
    SOURCE_FOLDER = "src"
    IGNORE_CLASSIFY = ["env"]
    PYTHON_ENV = ""
    CONFIG_PY_CLASSIFY = ["database", "cache"]

    def get_parsed_dict(self):
        """It returns complete dictionary to convert to yaml"""
        data = {k: v for k, v in self.get_dict().items() if v}

        env_data = data.get("env", None)

        if not env_data:
            self.__dict__["env"] = {}
            data["env"] = {}

        if not data["env"].get("SECRET_KEY", None):
            self.__dict__["env"]["SECRET_KEY"] = create_secret_key()
            data["env"]["SECRET_KEY"] = create_secret_key()

        return data

    def get_data_as_secret(self, key, classifier):
        """Return Data as Yaml Secret Data Form"""
        if classifier not in self.IGNORE_CLASSIFY:
            to_insert = {key: f"${classifier.upper()}_{key.upper()}"}
        else:
            to_insert = {key: f"${key.upper()}"}

        return to_insert

    def get_py_config_data(self, secret, key, cls_py, classifier):
        data = ""
        data += "'" if cls_py else ''
        data += key if classifier in self.CONFIG_PY_CLASSIFY else secret[key][1:]
        data += "'" if cls_py else ''
        data += " : " if cls_py else " = "
        data += f"os.environ.get('{secret[key][1:]}', '')"
        data += ",\n" if cls_py else ''
        return data

    def get_setup_yaml_data(self):
        """Creates YAML Data and makes database, cache and env as secret"""
        data = self.get_parsed_dict()
        env_data = ""
        for classifier in self.ENV_SECRET:
            if classifier in data and data[classifier]:
                cls_py = True if classifier in self.CONFIG_PY_CLASSIFY else False
                env_data += f"{classifier.upper()}_CONFIG=" + "{" if cls_py else ""
                for _id, (key, val) in enumerate(data[classifier].items()):
                    secret = self.get_data_as_secret(key, classifier)
                    data[classifier].update(secret)
                    env_data += self.get_py_config_data(secret, key, cls_py, classifier)
                    if _id == len(data[classifier].items()) - 1 and cls_py:
                        env_data += "}\n"
        self.PYTHON_ENV += env_data
        return data

    def create_setup_yaml(self):
        """Creates setup.yaml file"""
        with open(SETUP_CONFIG_FILE, "w") as file:
            yaml.dump(self.get_setup_yaml_data(), file, sort_keys=False)
            file.close()

    def create_env_secret(self):
        """Creates .env file"""
        data = self.get_parsed_dict()
        with open(ENV_FILE, "w") as env:
            for e in self.ENV_SECRET:
                if e in data and data[e]:
                    for k in data[e]:
                        if e not in self.IGNORE_CLASSIFY:
                            env.write(f"{e.upper()}_{k.upper()}={data[e][k]}\n")
                        else:
                            env.write(f"{k.upper()}={data[e][k]}\n")

    def generate_yaml_env(self):
        """Generate Yaml and Env File"""
        self.create_setup_yaml()
        self.create_env_secret()

    def normalize_name(self):
        """Normalize Name, Remove white spaces from name"""
        return self.name.replace(" ", "_")

    def set_py_from_template(self, template_name, py_file, data=None):
        """Create Django/Python File Using Templates"""
        _data = {"PROJECT_NAME": self.normalize_name()}
        if data:
            _data.update(**data)

        # Read Template File
        with open(f"{PATH.parent}/template/{template_name}", "r") as temp:
            template_data = temp.read()
        # Replace any variable in template file
        for key, text in _data.items():
            template_data = template_data.replace(f"${key}", text)

        with open(py_file, "w") as file:
            file.write(template_data)

    def get_all_libs(self):
        """Return All Installable Libs, [Remove any duplicate by converting it to set]"""
        libs = self.libraries if self.libraries else []
        libs += self.required if self.required else []
        return set(list(libs))

    def install_libraries(self, req_file=DEFAULT_REQUIREMENT_FILE):
        """Pip Install Libraries"""
        for lib in self.get_all_libs():
            execute(f"{pip_name()} install {lib}")

        current_dir = os.getcwd()
        file_name = req_file
        has_requirements = os.path.isfile("{}/{}".format(current_dir, file_name))
        if has_requirements:
            execute("pip3 install -r requirements.txt")

    def get_settings_installed_app(self):
        """Get Required Installed Libs in INSTALLED_APP Settings"""
        return "".join([f"   {INSTALLED_APP[lib]},\n" for lib in self.get_all_libs() if lib in INSTALLED_APP])

    def get_middlewares(self):
        """Set required middlewares in Middleware Settings"""
        return "".join([f"   {MIDDLEWARE[lib]},\n" for lib in self.get_all_libs() if lib in MIDDLEWARE])

    def get_extra(self):
        """Any Extra Settings"""
        return "".join([f"{EXTRA[lib]},\n" for lib in self.get_all_libs() if lib in EXTRA])

    def create_required_directory(self):
        """Create Folders That are required"""
        folders_to_create = [self.SOURCE_FOLDER,
                             f"{self.SOURCE_FOLDER}/media",
                             f"{self.SOURCE_FOLDER}/static",
                             f"{self.SOURCE_FOLDER}/template",
                             f"{self.SOURCE_FOLDER}/{self.normalize_name()}"]
        for folder in folders_to_create:
            os.mkdir(folder)

    def create_python_file(self):
        """Create Required Python Files"""
        APP_LOC = f"{self.SOURCE_FOLDER}/{self.normalize_name()}"

        def django_location(root_location, file_name, extension=".py", suffix=""):
            return f"{root_location}/{suffix}{file_name}{extension}"

        files = [
            {
                "name": "asgi",
                "dj_loc": APP_LOC,
                "data": {},
                "extension": ".py",
                "suffix": ""
            },
            {
                "name": "wsgi",
                "dj_loc": APP_LOC,
                "data": {},
                "extension": ".py",
                "suffix": ""
            },
            {
                "name": "settings",
                "dj_loc": APP_LOC,
                "data": {
                    "INSTALLED_APPS": self.get_settings_installed_app(),
                    "MIDDLEWARES": self.get_middlewares(),
                    "EXTRA": self.get_extra(),
                    "CACHE": """CACHE = {'default': CACHE_CONFIG}""" if self.cache else "",
                    "STATIC_SETTINGS": STATIC_FILE_SETTINGS if self.static else "",
                    "MEDIA_SETTINGS": MEDIA_FILE_SETTINGS if self.media_files else "",
                    "TEMPLATE_SETTINGS": TEMPLATE_SETTINGS if self.template else ""
                },
                "extension": ".py",
                "suffix": ""
            },
            {
                "name": "urls",
                "dj_loc": APP_LOC,
                "data": {},
                "extension": ".py",
                "suffix": ""
            },
            {
                "name": "manage",
                "dj_loc": self.SOURCE_FOLDER,
                "data": {},
                "extension": ".py",
                "suffix": ""
            },
            {
                "name": "config",
                "dj_loc": APP_LOC,
                "data": {
                    "CONFIG_VARS": self.PYTHON_ENV
                },
                "extension": ".py",
                "suffix": ""
            },
            {
                "name": "readme",
                "dj_loc": self.SOURCE_FOLDER,
                "data": {},
                "extension": ".md",
                "suffix": ""
            },
            {
                "name": "gitignore",
                "dj_loc": self.SOURCE_FOLDER,
                "data": {},
                "extension": "",
                "suffix": "."
            }
        ]
        for file in files:
            f_name = file.get("name")
            location = file.get("dj_loc")
            data = file.get("data")
            ext = file.get("extension")
            suf = file.get("suffix")
            self.set_py_from_template(
                f_name + ".template",
                django_location(file_name=f_name, root_location=location, extension=ext, suffix=suf),
                data=data
            )

    @staticmethod
    def create_requirements_file():
        execute("pip3 freeze > requirements.txt")

    @safe_create_dir
    def create_project(self):
        self.generate_yaml_env()
        tasks = [
            {
                "title": "Creating Source Folder",
                "task": self.create_required_directory
            },
            {
                "title": "Installing Libraries",
                "task": self.install_libraries
            },
            {
                "title": "Creating Project File",
                "task": self.create_python_file
            },
            {
                "title": "Creating Requirement File",
                "task": self.create_requirements_file
            }
        ]

        for key, task in enumerate(tasks):
            log(f"{key + 1}.. {task['title']}")
            task["task"]()
