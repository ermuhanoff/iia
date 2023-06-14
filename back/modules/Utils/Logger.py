from datetime import datetime
import inspect
import os


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class LEVELS:
    INFO = "INFO"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class Logger:
    @staticmethod
    def info(message: str) -> None:
        Logger.__print_message(message=message, level=LEVELS.INFO)

    @staticmethod
    def debug(message: str) -> None:
        Logger.__print_message(message=message, level=LEVELS.DEBUG)

    @staticmethod
    def error(message: str) -> None:
        Logger.__print_message(message=message, level=LEVELS.ERROR)

    @staticmethod
    def __print_message(message: str, level: str) -> None:
        time = datetime.now().strftime("%H:%M:%S")
        curframe = inspect.currentframe()

        outerframes = inspect.getouterframes(curframe, 2)

        file_name = os.path.basename(outerframes[2].filename)
        module_name = os.path.splitext(file_name)[0]
        function_name = outerframes[2].function

        color = Logger.__get_color_by_level(level)

        start_color_char = color if color is not None else ""
        end_color_char = bcolors.ENDC if color is not None else ""

        print(
            f"{start_color_char}[{level}] [{time}] {module_name}:{function_name} -> {message}{end_color_char}"
        )

    @staticmethod
    def __get_color_by_level(level: str) -> str | None:
        match level:
            case LEVELS.INFO:
                return bcolors.OKGREEN
            case LEVELS.DEBUG:
                return bcolors.OKCYAN
            case LEVELS.ERROR:
                return bcolors.FAIL
