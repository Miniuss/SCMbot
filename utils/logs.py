from enum import Enum
from datetime import datetime

logged_this_instance = False

class Colors(Enum):
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
    def __init__(self, color: Colors, title: str):
        self.color = color
        self.title = title

LL_INFO = LogLevel(Colors.cyan, "INFO")
LL_WARN = LogLevel(Colors.yellow, "WARN")
LL_ERROR = LogLevel(Colors.red, "ERROR")

def _time_now():
    current_time = datetime.now()
    
    date = f"{str(current_time.day).zfill(2)}/{str(current_time.month).zfill(2)}/{current_time.year}"
    time = f"{str(current_time.hour).zfill(2)}:{str(current_time.minute).zfill(2)}:{str(current_time.second).zfill(2)}.{str(current_time.microsecond).zfill(6)}"

    return f"{date} {time}"

def log(info: str, log_level: LogLevel = LL_INFO):
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

info = lambda info: log(info, LL_INFO)
warn = lambda info: log(info, LL_WARN)
error = lambda info: log(info, LL_ERROR)

if __name__ == "__main__":
    if input("Start test? [Y/N]: ").upper() == "Y":
        log("Logging via \"log\" method", LL_INFO)
        info("Logging via \"info\" lambda")
        warn("Logging via \"warn\" lambda")
        error("Logging via \"error\" lambda")
