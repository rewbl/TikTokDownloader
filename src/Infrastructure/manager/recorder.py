from pathlib import Path
from platform import system

from src.Infrastructure.module import ColorfulConsole

__all__ = ["DownloadRecorder"]


class DownloadRecorder:
    encode = "UTF-8-SIG" if system() == "Windows" else "UTF-8"

    def __init__(
            self,
            switch: bool,
            folder: Path,
            console: ColorfulConsole):
        self.switch = switch
        self.path = folder.joinpath("IDRecorder.txt")
        self.file = None
        self.console = console
        self.record = self.__get_set()

    def __get_set(self) -> set:
        return self.__read_file() if self.switch else set()

    def __read_file(self):
        if not self.path.is_file():
            blacklist = set()
        else:
            with self.path.open("r", encoding=self.encode) as f:
                blacklist = self.__restore_data({line.strip() for line in f})
        self.file = self.path.open("w", encoding=self.encode)
        return blacklist

    def __save_file(self, file):
        file.write("\n".join(f"{i}" for i in self.record))

    def update_id(self, id_):
        if self.switch:
            self.record.add(id_)


    def close(self):
        if self.file:
            self.__save_file(self.file)
            self.file.close()
            self.file = None
            # print("Close IDRecorder")  # 调试代码

    def __restore_data(self, ids: set) -> set:
        return ids

