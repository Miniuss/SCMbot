"""
# logs.py
Module designed for the simpliest logging system.
"""

from enum import Enum
from datetime import datetime

logged_this_instance = False

class Colors(Enum):
    """
    # Colors (enum class)
    Enum class containing ANSI color codes.

    Available colors are: black, red, green, yellow, blue, purple, cyan, white. Another
    option is `reset` that will reset every color parameter for text.
    """

    black  = "\033[0;30m"
    red    = "\033[0;31m"
    green  = "\033[0;32m"
    yellow = "\033[0;33m"
    blue   = "\033[0;34m"
    purple = "\033[0;35m"
    cyan   = "\033[0;36m"
    white  = "\033[0;37m"
    reset  = "\033[0m"

class LogLevel():
    """
    # LogLevel
    A simple class containing log level type information such as its color (for title)
    and the title's text.
    """

    def __init__(self, color: Colors, title: str):
        """
        ## LogLevel __init__
        Initiates `LogLevel` class with log level's parameters.

        ### Arguments
        color: `Colors` class' enum. Used to color the title for log level.

        title: String that represents log level's title (ex. "INFO" or "WARN")
        """

        self.color = color
        self.title = title

LL_INFO = LogLevel(Colors.cyan, "INFO")
LL_WARN = LogLevel(Colors.yellow, "WARN")
LL_ERROR = LogLevel(Colors.red, "ERROR")

def _time_now():
    """
    # _time_now
    Method returning current timestamp in `DD/MO/YY HH:MM:SS.MS` format.
    """

    current_time = datetime.now()
    formatted_time = current_time.strftime(r"%d/%m/%Y %H:%M:%S.%f")

    return formatted_time

def log(info: str, log_level: LogLevel = LL_INFO):
    """
    # log
    Method that outputs info into console and `logs.log` file with datetime 
    and log level type.

    ### Arguments
    info: String representing info that will be printed onto console and written into file

    log_level: `LogLevel` class that will define level of this log. By default: preset `LL_INFO` log level, that stands for standart "INFO" log level.
    """

    global logged_this_instance

    time = _time_now()
    title = log_level.title

    log_text = f"{Colors.purple.value}{time}{Colors.reset.value} {log_level.color.value}{title}:{Colors.reset.value} {info}"
    monochrome_log_text = f"{time} {title}: {info}"

    print(log_text)

    with open("logs.log", "a", encoding="utf-8") as logs:
        if not logged_this_instance:
            logged_this_instance = True
            logs.write(f"\n[NEW LAUNCH AT {time}]\n")

        logs.write(f"{monochrome_log_text}\n")

def info(info: str):
    """
    # info (method)
    Shortcut function to call `log` with "INFO" log level.

    ### Arguments
    info: String representing info that will be printed onto console and written into file
    """
    
    log(info, LL_INFO)

def warn(info: str):
    """
    # warn (method)
    Shortcut function to call `log` with "WARN" log level.

    ### Arguments
    info: String representing info that will be printed onto console and written into file
    """

    log(info, LL_WARN)

def error(info: str):
    """
    # error (method)
    Shortcut function to call `log` with "ERROR" log level.

    ### Arguments
    info: String representing info that will be printed onto console and written into file
    """

    log(info, LL_ERROR)

if __name__ == "__main__":
    if input("Start test? [Y/N]: ").upper() == "Y":
        log("Logging via \"log\" method", LL_INFO)
        info("Logging via \"info\" lambda")
        warn("Logging via \"warn\" lambda")
        error("Logging via \"error\" lambda")
