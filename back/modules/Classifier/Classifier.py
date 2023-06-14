import os
import random
import yaml

from typing import Any, Callable
from fuzzywuzzy import fuzz
from modules.HtmlParser.HtmlParser import HtmlParser
from data.sstu_data import what_is_instit, what_is_sstu, where_is, who_are_you


class EntityObject:
    def __init__(
        self, entity_group: str = "", entity: str = "", percent: int = 0, entity_data: dict[str, str] | None = None
    ) -> None:
        self.entity_group: str = entity_group
        self.entity: str = entity
        self.percent: int = percent
        self.entity_data: dict[str, str] | None = entity_data


class CommandObject:
    def __init__(self, command: str = "", percent: int = 0, is_now: str = "") -> None:
        self.command: str = command
        self.percent: int = percent
        self.is_now: str = is_now


class Classifier:
    group_thershhold: int = 60
    teacher_thershhold: int = 65
    command_thershhold: int = 60

    def __init__(self) -> None:
        self.dictionaries_path: str = os.path.realpath("modules/Classifier/dictionaries/")

        self.COMMANDS_DICT: dict[str, list[str]] = yaml.safe_load(
            open(self.dictionaries_path + "/commands.yaml", "rt", encoding="utf8")
        )
        self.ENTITY_GROUP_KEYWORDS_DICT: dict[str, list[str]] = yaml.safe_load(
            open(
                self.dictionaries_path + "/entity_groups_keywords.yaml",
                "rt",
                encoding="utf8",
            )
        )
        self.ENTITIES_DICT: dict[str, list[dict[str, dict[str, str] | None]]] = yaml.safe_load(
            open(self.dictionaries_path + "/entities.yaml", "rt", encoding="utf8")
        )
        self.VARIATE_ANSWERS_DICT: dict[str, list[str]] = yaml.safe_load(
            open(self.dictionaries_path + "/variate_answers.yaml", "rt", encoding="utf8")
        )

    def __get_variate_answer(self, command: str) -> str:
        list_of_answers = self.VARIATE_ANSWERS_DICT[command]

        random_index_of_answer = random.choice(range(len(list_of_answers)))

        return list_of_answers[random_index_of_answer]

    def __find_entity_group_by_keyword(self, question: str) -> str:
        prev_entity_group_name = ""
        prev_percent = 0
        percent_threshold = 65
        for (
            entity_group_name,
            entity_group_keywords,
        ) in self.ENTITY_GROUP_KEYWORDS_DICT.items():
            for entity_group_keyword in entity_group_keywords:
                result = fuzz.partial_ratio(entity_group_keyword, question)

                if result > prev_percent:
                    prev_entity_group_name = entity_group_name
                    prev_percent = result
        return prev_entity_group_name if prev_percent >= percent_threshold else ""

    def __recognize_entity(self, question: str) -> EntityObject:
        entity_object = EntityObject()

        def _recognize_entity(
            question: str,
            entity_group_name: str,
            entity_group_array: list[dict[str, dict[str, str] | None]],
        ):
            for entity in entity_group_array:
                dict_from_entity = entity.items()
                entity_name, entity_data = list(dict_from_entity)[0]
                result = fuzz.partial_ratio(entity_name.lower(), question.lower())

                if result > entity_object.percent:
                    entity_object.entity_group = entity_group_name
                    entity_object.entity = entity_name
                    entity_object.percent = result
                    entity_object.entity_data = entity_data
            return entity_object

        group_name = self.__find_entity_group_by_keyword(question)

        if group_name != "":
            _recognize_entity(question, group_name, self.ENTITIES_DICT[group_name])
        else:
            for entity_group_name, entity_group_array in self.ENTITIES_DICT.items():
                _recognize_entity(question, entity_group_name, entity_group_array)

        return entity_object

    def __recognize_command(self, question: str) -> CommandObject:
        command_object = CommandObject()

        if fuzz.partial_ratio("сейчас", question) > 70:
            command_object.is_now = "time"
        if fuzz.partial_ratio("сегодня", question) > 70:
            command_object.is_now = "day"

        for command, key_words in self.COMMANDS_DICT.items():
            for key_word in key_words:
                result = fuzz.partial_ratio(key_word.lower(), question.lower())

                if result > command_object.percent:
                    command_object.command = command
                    command_object.percent = result
        return command_object

    def __get_answer(self, command_object: CommandObject, entity_object: EntityObject) -> str:
        command_is_now_flag = command_object.is_now
        command_percent = command_object.percent
        command = command_object.command
        entity_group = entity_object.entity_group
        entity_percent = entity_object.percent
        entity_data = entity_object.entity_data
        entity = entity_object.entity

        if command_percent < self.command_thershhold:
            return self.__get_variate_answer("not_found")

        match command:
            case "rasp":
                if entity_group == "group":
                    if entity_percent >= self.group_thershhold and entity_data is not None:
                        rasp = HtmlParser.get_rasp(entity_group, int(entity_data["id"]), command_is_now_flag)

                        if command_is_now_flag == "day":
                            if rasp == "":
                                return f"Сегодня для группы {entity} нет пар!"
                            return f"Сегодня для группы {entity} вот такие пары:{rasp}"
                        elif command_is_now_flag == "time":
                            if rasp == "":
                                return f"Сейчас у группы {entity} нет никакой пары!"
                            return f"Сейчас у группы {entity} идёт эта пара:{rasp}"
                        return f'{self.__get_variate_answer("rasp")} для группы {entity}!{rasp}'
                    else:
                        return self.__get_variate_answer("not_found_rasp_group")
                elif entity_group == "teacher":
                    if entity_percent >= self.teacher_thershhold and entity_data is not None:
                        rasp = HtmlParser.get_rasp(entity_group, int(entity_data["id"]), command_is_now_flag)

                        if command_is_now_flag == "day":
                            if rasp == "":
                                return f"Сегодня у преподавателя {entity} нет пар!"
                            return f"Сегодня у преподавателя {entity} вот такие пары:{rasp}"
                        elif command_is_now_flag == "time":
                            if rasp == "":
                                return f"Сейчас у преподавателя {entity} нет никакой пары!"
                            return f"Сейчас у преподавателя {entity} идёт эта пара:{rasp}"
                        return f'{self.__get_variate_answer("rasp")} для преподавателя {entity}!{rasp}'
                    else:
                        return self.__get_variate_answer("not_found_rasp_teacher")
            case "info":
                return f"Вот информация о {entity}!"
            case "hello":
                return self.__get_variate_answer(command)
            case "how_are_you":
                return self.__get_variate_answer(command)
            case "what_is":
                if entity_group == "sstu_main":
                    return what_is_sstu
                elif entity_group == "sstu_instit":
                    return what_is_instit
            case "who_are_you":
                return who_are_you
            case "where_is":
                if entity_group == "sstu_main":
                    return where_is
                return "К сожалению, не знаю где это находится"

        return self.__get_variate_answer("not_found")

    def classify(self, command: str, body: str, callback: Callable[[str], Any]) -> None:
        command_object: CommandObject = self.__recognize_command(body)
        entity_object: EntityObject = self.__recognize_entity(body)

        answer = self.__get_answer(command_object, entity_object)

        callback(answer)
