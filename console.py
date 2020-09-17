import math
import time
from colorama import Fore
import re


class Console:
    lastTimestamp = -1
    disabled = False
    logPath = None

    def __init__(self, maxLength=64) -> None:
        self.maxLength = maxLength

    def log(self, text: str = None, color=None, begin=False) -> float:
        if self.disabled:
            return
        maxLength = self.maxLength
        if text is None:
            text = "".ljust(maxLength, "-")
        t = time.time()
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
        for i in range(len(textList)):
            ti = textList[i]
            if i == 0:
                ti = Console.coloredText(ti, color)
                ti = f"{Console.coloredText(timeStamp, Fore.BLUE)} {ti}"
            elif i == len(textList) - 1:
                ti = Console.strAlign(ti, maxLength + timeStampLen + 1, "R")
                ti = Console.coloredText(ti, color)
            else:
                ti = "".ljust(timeStampLen + 10) + ti
                ti = Console.coloredText(ti, color)
            print(ti)
            if self.logPath:
                with open(self.logPath, "a", encoding="utf-8") as file:
                    file.write(Console.removeTextColor(ti) + "\n")
        self.lastTimestamp = t
        return t

    def success(self, text: str, begin=False):
        return self.log("SUCCESS: " + text, Fore.GREEN, begin)

    def warning(self, text: str, begin=False):
        return self.log("WARNING: " + text, Fore.YELLOW, begin)

    def error(self, text: str = None, begin=False):
        return self.log("ERROR  : " + text, Fore.RED, begin)

    def info(self, text: str = None, begin=False):
        return self.log("INFO   : " + text, Fore.CYAN, begin)

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
