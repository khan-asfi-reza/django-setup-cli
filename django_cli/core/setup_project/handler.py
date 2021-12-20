import os
from typing import Optional

import yaml

from django_cli.config import DATABASE_DRIVERS, LINKED_LIBRARY
from django_cli.const import (GENERATE_LOG_SUCCESS_MSG,
                              YAML_PARSE_ERROR_MSG,
                              FILE_NOT_FOUND,
                              CONFIG_FILE_NAME,
                              LOG_SUCCESS_PROJECT_COMPLETE, DEFAULT_REQUIREMENT_FILE)
from django_cli.core.BaseCommand import BaseCommand, pre_execute
from django_cli.core.setup_project.model import (SetupProjectState,
                                                 DBConfig,
                                                 CacheConfig,
                                                 DefaultDBConfig)
from django_cli.core.setup_project.prompt import PromptConfig
from django_cli.utils import error, success


class ProjectInitializer(BaseCommand):
    state = None

    def __init__(self, project_name=""):
        self.project_name = project_name
        self.default = False

    def create_data_set(self, dict_data: dict) -> None:
        """
        Creates Project Config Dataset from YAML / CLI
        :param dict_data: dict
        :return:
        """
        # Default Dataset
        database_config = DefaultDBConfig
        cache_config = None
        # Dictionary Dataset
        dict_data.pop("required", None)
        required = []
        db: Optional[dict] = dict_data.pop("database", None)
        cache: Optional[dict] = dict_data.pop("cache", None)
        libraries: Optional[list] = dict_data.get("libraries", [])

        # Add required library to the required library list
        required = required + [LINKED_LIBRARY[item] for item in libraries if item in LINKED_LIBRARY]

        # If Database exists in dictionary, Create Database Config
        try:
            # Create Database Config
            if db:
                database_config = DBConfig(**db)
                required += [val for key, val in DATABASE_DRIVERS.items() if key == database_config.engine]
            # Create Cache Config
            if cache:
                cache_config = CacheConfig(**cache)
        except TypeError as t:
            error("Invalid Config Data - {}".format(t.__str__()))

        # Set State
        required = set(required)
        self.state = SetupProjectState(**dict_data, database=database_config, cache=cache_config,
                                       required=list(required))

    @staticmethod
    def get_yaml_config(file_name):
        # Parse YAML File
        try:
            with open(file_name, 'r') as stream:
                try:
                    # Safe Load
                    parsed_yaml = yaml.safe_load(stream)
                    if parsed_yaml:
                        parsed_yaml = {k.lower(): v for k, v in parsed_yaml.items()}
                    else:
                        raise yaml.YAMLError
                    # Return parsed yaml
                    return parsed_yaml
                except yaml.YAMLError or AttributeError:
                    error(YAML_PARSE_ERROR_MSG)
                    return {}
        except FileNotFoundError:
            error(FILE_NOT_FOUND)
            return {}

    @pre_execute()
    def enquire(self):
        # Get yaml File
        current_dir = os.getcwd()
        file_name = CONFIG_FILE_NAME
        has_yaml = os.path.isfile("{}/{}".format(current_dir, file_name))
        # If Yaml
        if has_yaml:
            yaml_file = self.get_yaml_config(file_name)
            if yaml_file:
                self.create_data_set(yaml_file)
                return
        # Create Using CLI
        self.create_data_set(PromptConfig(project_name=self.project_name).execute())

    @BaseCommand.execute
    def generate(self):
        """Generates Setup YAML File"""
        self.state.generate_yaml_env()
        success(GENERATE_LOG_SUCCESS_MSG)

    @BaseCommand.execute
    def start_project(self):
        """Starts Django Project"""
        self.state.create_project()
        success(LOG_SUCCESS_PROJECT_COMPLETE)

    @BaseCommand.execute
    def install_libraries(self, req_file=DEFAULT_REQUIREMENT_FILE):
        """Install Libraries"""
        self.state.install_libraries(req_file=req_file)
