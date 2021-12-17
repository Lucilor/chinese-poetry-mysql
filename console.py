import json
import math
import re
import time
from typing import Any, Union

from colorama import Fore, init

init()


class Console:
    lastTimestamp = -1
    disabled = False
    logPath: Union[str, None] = None
    indent = 4

    def __init__(self, maxLength=64) -> None:
        self.maxLength = maxLength

    def log(
        self,
        text: Any = None,
        color: Union[str, None] = None,
        begin: Union[float, None] = False,
        indent: int = 0,
        prefix: str = "",
        lock: Any = None,
    ):
        t = time.time()
        if self.disabled:
            return t
        if lock:
            lock.acquire()
            try:
                return self.log(text, color, begin, indent, prefix)
            finally:
                lock.release()
        typeText = type(text)
        if typeText != str:
            if isinstance(text, (tuple, list)):
                return self.log("\n".join(text), color, begin, indent, prefix)
            elif text is not None:
                try:
                    text = json.dumps(text, ensure_ascii=False)
                except:
                    text = str(text)
                return self.log(text, color, begin, indent, prefix)
        maxLength = self.maxLength
        if text is None:
            text = "".ljust(maxLength, "-")
        if type(text) != str:
            raise Exception("text type error")
        now = time.localtime(t)
        h = str(now.tm_hour).zfill(2)
        m = str(now.tm_min).zfill(2)
        s = str(now.tm_sec).zfill(2)
        textList = text.split("\n")
        if begin is True:
            begin = self.lastTimestamp
        elif begin is not False and isinstance(begin, int) or isinstance(begin, float):
            begin = float(begin)
        else:
            begin = None
        if begin is not None:
            length = maxLength - Console.strLen(textList[-1])
            timeText = Console.strAlign(f"{Console.round(t-begin)}s", length, "R")
            # timeText = Console.coloredText(timeText, color)
            textList[-1] += timeText
        timeStamp = f"[{h}:{m}:{s}]"
        timeStampLen = Console.strLen(timeStamp)
        if indent == True:
            indent = self.indent
        for i in range(len(textList)):
            if not textList[i]:
                continue
            ti = prefix + " " * indent * i + textList[i]
            if i == 0:
                ti = Console.coloredText(ti, color)
                ti = f"{Console.coloredText(timeStamp, Fore.BLUE)} {ti}"
            # elif i == len(textList) - 1:
            #     ti = Console.strAlign(ti, maxLength + timeStampLen + 1, "R")
            #     ti = Console.coloredText(ti, color)
            else:
                ti = "".ljust(timeStampLen + 1) + ti
                ti = Console.coloredText(ti, color)
            print(ti)
            if self.logPath:
                with open(self.logPath, "a", encoding="utf-8") as file:
                    file.write(Console.removeTextColor(ti) + "\n")
        self.lastTimestamp = t
        return t

    def success(self, text=None, begin=False, indent=0, lock=None):
        return self.log(text, Fore.GREEN, begin, indent, "SUCCESS: ", lock)

    def warning(self, text=None, begin=False, indent=0, lock=None):
        return self.log(text, Fore.YELLOW, begin, indent, "WARNING: ", lock)

    def error(self, text=None, begin=False, indent=0, lock=None):
        return self.log(text, Fore.RED, begin, indent, "ERROR  : ", lock)

    def info(self, text=None, begin=False, indent=0, lock=None):
        return self.log(text, Fore.CYAN, begin, indent, "INFO   : ", lock)

    @staticmethod
    def strLen(text: str):
        length = len(text)
        for char in text:
            if "\u4e00" <= char <= "\u9fa5":
                length += 1
        return length
        # try:
        #     return len(text.encode("utf-8"))
        # except:
        #     return None

    @staticmethod
    def strAlign(text: str, length: int, type: str):
        spaceNum = length - Console.strLen(text)
        if type == "L":
            left = 0
            right = spaceNum
        elif type == "R":
            left = spaceNum
            right = 0
        else:
            left = spaceNum // 2
            right = spaceNum - left
        return " " * left + text + " " * right

    @staticmethod
    def round(num, bits=2):
        num = float(num)
        decimalPart = num - math.floor(num)
        if decimalPart == 0:
            leadingZeros = 0
        else:
            leadingZeros = max(0, -math.ceil(math.log10(num - math.floor(num))))
        return round(num, leadingZeros + bits)

    @staticmethod
    def coloredText(text: str, color):
        if color is None:
            return text
        else:
            return f"{color}{text}{Fore.RESET}"

    @staticmethod
    def removeTextColor(text: str):
        return re.sub(r"\x1b\[[0-9]+m", "", text)


console = Console()
