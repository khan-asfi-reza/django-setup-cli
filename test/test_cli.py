import os
import shutil
from unittest import TestCase
from click.testing import CliRunner
from django_cli.cli import make_generate, start_project, install_libraries

GENERATE_TEST_INPUT = "Project1\ny\ny\ny\ny\ny\ny\ny\ny\nn\ny\nn\ny\ny\ny\ny\n2\nX\nY\nZ\nA\nB\nn"


class TestCLI(TestCase):
    path = os.getcwd()

    def delete_requirement(self):
        try:
            os.remove(f"{self.path}/requirements.txt")
        except FileNotFoundError:
            pass

    def test_generate(self):
        runner = CliRunner()
        result = runner.invoke(make_generate, input=GENERATE_TEST_INPUT)
        self.assertEqual(result.exit_code, 0)
        self.delete_requirement()

    def test_generate_project(self):
        runner = CliRunner()
        result = runner.invoke(start_project, input=GENERATE_TEST_INPUT)
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(install_libraries)
        self.assertEqual(result.exit_code, 0)
        self.delete_requirement()


    def test_regenerate(self):
        self.test_generate_project()
        self.test_generate_project()
        self.delete_requirement()

    def tearDown(self) -> None:
        os.remove(f"{self.path}/setup.yaml")
        os.remove(f"{self.path}/.env")
        if os.path.isdir(f"{self.path}/src"):
            shutil.rmtree(self.path + "/src")


class TestCliWithArgs(TestCase):
    path = os.getcwd()

    def delete_requirement(self):
        try:
            os.remove(f"{self.path}/requirements.txt")
        except FileNotFoundError:
            pass

    def tearDown(self) -> None:
        os.remove(f"{self.path}/setup.yaml")
        os.remove(f"{self.path}/.env")
        if os.path.isdir(f"{self.path}/src"):
            shutil.rmtree(self.path + "/src")

    def test_generate(self):
        runner = CliRunner()
        result = runner.invoke(make_generate, ["PROJECTNAME"], input=GENERATE_TEST_INPUT)
        self.assertEqual(result.exit_code, 0)
        self.delete_requirement()