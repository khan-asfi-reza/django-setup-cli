import os
from unittest import TestCase

from django_cli.setup_project.handler import ProjectInitializer
from django_cli.setup_project.model import DefaultDBConfig


class ErrorTest(TestCase):
    BASE_DIR = os.getcwd()

    def test_errors(self):
        Proj = ProjectInitializer()
        Proj.create_data_set(
            {
                "name": "Pr",
                "docker": True,
                "database": "DATABASE",
                "cache": "Cache"
            }
        )

        self.assertEqual(Proj.state.database.engine, DefaultDBConfig.engine)
        self.assertIsNone(Proj.state.cache)

    def test_yaml(self):
        data = ProjectInitializer.get_yaml_config(self.BASE_DIR + "/tests/nothing.yaml")
        self.assertEqual(data, {})

    def test_bad_yaml(self):
        data = ProjectInitializer.get_yaml_config(self.BASE_DIR + "/tests/bad.yaml")
        self.assertEqual(data, {})

    def test_invalid_yaml(self):
        data = ProjectInitializer.get_yaml_config(self.BASE_DIR + "/tests/bad.txt")
        self.assertEqual(data, {})

    def test_empty_yaml(self):
        data = ProjectInitializer.get_yaml_config(self.BASE_DIR + "/tests/empty.yaml")
        self.assertEqual(data, {})