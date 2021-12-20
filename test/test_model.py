import os.path

from django_cli.core.setup_project.model import DBConfig, CacheConfig, SetupProjectState, SETUP_CONFIG_FILE, ENV_FILE
from unittest import TestCase


class DataStateTest(TestCase):
    DB_CONFIG = {
        "engine": "postgresql",
        "user": "postgres",
        "password": "password",
        "host": "localhost",
        "port": "5432",
        "option": {
            "CONFIG": "CONFIG"
        }
    }

    CACHE_CONFIG = {
        "backend": "redis",
        "location": "localhost",
    }

    PROJECT_CONFIG = {
        "name": "TEST_PROJECT",
        "libraries": ["django-rest-framework", "celery"],
        "docker": True,
        "requirements": True,
        "template": True,
        "media": False,
        "static": False
    }

    def setUp(self) -> None:
        self.db_config = DBConfig(**self.DB_CONFIG)
        self.cache_config = CacheConfig(**self.CACHE_CONFIG)
        self.project_config = SetupProjectState(**self.PROJECT_CONFIG, database=self.db_config, cache=self.cache_config)

    def config_tester(self, config, config_data):
        items = config_data.keys()
        dumped_data = config.dump_upper()
        for item in items:
            self.assertEqual(dumped_data[str(item).upper()], config_data[item])

    def test_db_config(self):
        self.config_tester(self.db_config, self.DB_CONFIG)

    def test_cache_config(self):
        self.config_tester(self.cache_config, self.CACHE_CONFIG)

    def test_yaml_generate(self):
        path = os.path.curdir
        # Create Test Setup YAML Config
        self.project_config.create_setup_yaml()
        # Create ENV Secret File
        self.project_config.create_env_secret()
        # Test If File exists
        self.assertEqual(os.path.isfile(f"./{SETUP_CONFIG_FILE}"), True)
        self.assertEqual(os.path.isfile(f"./{ENV_FILE}"), True)
        # Read File None
        with open(f"./{SETUP_CONFIG_FILE}", "r") as config_file:
            data = config_file.read()
            self.assertIsNotNone(data)
        # Read Env File
        with open(f"./{ENV_FILE}", "r") as env_file:
            # Env File -> SECRET_KEY=test_secret_key\nENV_VAR=env_var
            data = env_file.read()
            # env_data -> ["SECRET_KEY=test_secret_key", "ENV_VAR=env_var"]
            env_data = data.split("\n")
            # env -> {SECRET_KEY: test_secret_key}
            env = {}
            for _data in env_data:
                _env = _data.split("=")
                env.update(
                    {
                        _env[0]: "".join(_env[1:])
                    }
                )
            self.assertEqual(env["SECRET_KEY"], self.project_config.get_parsed_dict()["env"]["SECRET_KEY"])
            self.assertEqual(env["DATABASE_ENGINE"], self.project_config.database.engine)
            self.assertEqual(env["CACHE_BACKEND"], self.project_config.cache.backend)
            self.assertIsNotNone(data)

