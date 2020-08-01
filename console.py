from math import ceil, floor
import math
import time
from colorama import Fore


class Console:
    lastTimestamp = -1
    disabled = False

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
        timeStamp = Console.coloredText(f"[{h}:{m}:{s}]", Fore.BLUE)
        if begin is True:
            begin = self.lastTimestamp
        elif begin is not False and isinstance(begin, int) or isinstance(begin, float):
            begin = float(begin)
        else:
            begin = None
        if begin is not None:
            length = maxLength - Console.strLen(text)
            text += Console.strAlign(f"{Console.round(t-begin)}s", length, "R")
        if color is not None:
            text = Console.coloredText(text, color)
        text = f"{timeStamp} {text}"
        print(text)
        self.lastTimestamp = t
        return t

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
    def round(num):
        num = float(num)
        decimalPart = num - floor(num)
        if decimalPart == 0:
            leadingZeros = 0
        else:
            leadingZeros = max(0,-ceil(math.log10(num - floor(num))))
        return round(num, leadingZeros + 2)

    @staticmethod
    def coloredText(text: str, color):
        return f"{color}{text}{Fore.RESET}"


console = Console()
