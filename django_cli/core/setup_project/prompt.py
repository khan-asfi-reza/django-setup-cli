from collections import ChainMap
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Any, Union, List

import click

from django_cli.config import LIBRARIES_OPTIONAL, DBEngine, CACHE_BACKED
from django_cli.core.setup_project.model import DefaultDBConfig
from django_cli.utils import log, success


class InputType(Enum):
    STRING = auto()
    MULTIPLE_CHOICE = auto()
    CHOICE = auto()
    INTEGER = auto()
    BOOLEAN = auto()
    GROUP = auto()
    LOG = auto()


@dataclass
class PromptLog:
    title: str
    text: str

    def execute(self):
        log(self.text)


@dataclass
class QuestionAbstract:
    """
        :arg
            name: Name of Question,
             input_type=InputType.STRING,that will be printed on the client side
            var: Variable Name that will be stored
            type: Data Type -> Option [str, int, bool]
            input_type: Generic Input Types
            Integer will not ask for confirmation and proceed forward
            options: List of options that can be selected
            prefix: Option Installation Prefix that will be shown on the client side
            children: List of child question
            title: To show Title

    """
    name: str
    var: str
    type: type = str
    input_type: Optional[InputType] = None
    required: bool = True
    options: List[Any] = None
    default: Any = ""
    prefix: str = ""
    title: str = ""
    children: Optional[List[Any]] = None

    def prompt(self, text, fg="blue", data_type: Any = None, **kwargs) -> Any:
        """
        :param data_type:
        :param fg: Foreground Color
        :param text: Prompt Text
        :return:
        """
        # Default Style
        text = click.style(text, fg=fg, **kwargs)

        # Use Instance Type
        data_type = self.type if not data_type else data_type

        if data_type is bool:
            return click.confirm(text)

        user_input = click.prompt(text, type=data_type)
        # Enforce Default Value
        return self.default if not user_input else user_input

    @staticmethod
    def log_list(lst):
        for key, data in enumerate(lst):
            log(f"{key + 1}. {data}")

    def execute(self) -> dict:
        """
        Returns Answer Dictionary
        """
        answer = {}

        # Input Type String | Boolean ->
        if self.input_type == InputType.STRING or self.input_type == InputType.BOOLEAN:
            answer = {self.var: self.prompt(self.name)}

        # IF Input is not required, seek confirmation
        proceed = True
        if not self.required:
            proceed = self.prompt(self.name, data_type=bool)

        # If Confirmed
        if proceed:
            # If Input Type Multiple Choice -> Create List of Selected Choices
            if self.input_type == InputType.MULTIPLE_CHOICE:
                choices = [choice for key, choice in enumerate(self.options)
                           if self.prompt(f"{key + 1}.{self.prefix} {choice}", data_type=bool)]
                answer = {self.var: choices}

            elif self.input_type == InputType.CHOICE:
                # Choice From Multiple List Log Choices
                self.log_list(self.options)

                while True:
                    user_input = self.prompt(f"{self.name}", data_type=int)
                    if len(self.options) >= int(user_input) > 0:
                        break

                answer = {self.var: list(self.options)[user_input - 1]}

            elif self.input_type == InputType.GROUP:
                answer = {self.var: dict(ChainMap(*[child.execute() for child in self.children]))}

        return answer


@dataclass
class Question(QuestionAbstract):
    pass


class PromptConfig:
    # Prompt Question
    PROMPT_QUES: List[Union[Question, PromptLog]] = [
        Question(
            input_type=InputType.STRING,
            title="Project Name",
            name="Your Project Name",
            var="name",
            default="Django Project"
        ),
        # Question(
        #     input_type=InputType.BOOLEAN,
        #     title="Dockerize",
        #     name="Enable Docker",
        #     var="docker",
        #     default=False,
        #     type=bool
        # ),
        Question(
            input_type=InputType.MULTIPLE_CHOICE,
            title="Install Necessary Libraries",
            name="Install Libraries",
            var="libraries",
            default=None,
            type=list,
            options=LIBRARIES_OPTIONAL,
            prefix="Install",
            required=False
        ),
        Question(
            input_type=InputType.BOOLEAN,
            title="Static File",
            name="Create/Use Static File",
            var="static",
            default=True,
            type=bool
        ),
        Question(
            input_type=InputType.BOOLEAN,
            title="Template File",
            name="Create/Use Template File",
            var="template",
            default=True,
            type=bool
        ),
        Question(
            input_type=InputType.BOOLEAN,
            title="Media File",
            name="Create/Use Media File",
            var="media",
            default=True,
            type=bool
        ),
        Question(
            input_type=InputType.GROUP,
            title="Setup Database",
            name="Setup Database [Skip To Use Default]",
            var="database",
            default=DefaultDBConfig,
            type=dict,
            required=False,
            children=[
                Question(
                    input_type=InputType.CHOICE,
                    name="Database Engine",
                    type=int,
                    options=DBEngine.keys(),
                    var="engine",
                ),
                Question(
                    input_type=InputType.STRING,
                    name="Database Name",
                    type=str,
                    var="name"
                ),
                Question(
                    input_type=InputType.STRING,
                    name="Database User",
                    type=str,
                    var="user"
                ),
                Question(
                    input_type=InputType.STRING,
                    name="Database Password",
                    type=str,
                    var="password"
                ),
                Question(
                    input_type=InputType.STRING,
                    name="Database Host",
                    type=str,
                    var="host"
                ),
                Question(
                    input_type=InputType.STRING,
                    name="Database Port",
                    type=str,
                    var="port"
                )
            ]
        ),
        Question(
            input_type=InputType.GROUP,
            title="Setup Cache",
            name="Install Cache",
            var="cache",
            default=None,
            type=dict,
            required=False,
            children=[
                Question(
                    input_type=InputType.CHOICE,
                    name="Cache Engine",
                    var="backend",
                    type=int,
                    options=CACHE_BACKED.keys(),
                ),
                Question(
                    input_type=InputType.STRING,
                    name="Cache Location",
                    type=str,
                    var="location"
                ),
            ]
        ),
    ]
    answer = {}

    def __init__(self, project_name):
        self.project_name = project_name
        if self.project_name:
            self.PROMPT_QUES.pop(0)
            self.PROMPT_QUES.insert(0, PromptLog(title="Project Name", text=f"Project Name :- {self.project_name}"))
            self.answer.update({"name": self.project_name})

    def execute(self):
        __answer = {}

        for key, val in enumerate(self.PROMPT_QUES):
            success(f"{key + 1}. {val.title}")
            data = val.execute()
            if data:
                __answer.update(data)

        return {k: v for k, v in __answer.items() if v}
