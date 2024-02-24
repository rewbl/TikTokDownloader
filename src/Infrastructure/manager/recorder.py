from pathlib import Path
from platform import system

from src.Infrastructure.custom import (
    ERROR,
    WARNING,
    INFO,
)
from src.Infrastructure.module import ColorfulConsole

__all__ = ["DownloadRecorder"]


class DownloadRecorder:
    encode = "UTF-8-SIG" if system() == "Windows" else "UTF-8"

    def __init__(
            self,
            switch: bool,
            folder: Path,
            state: bool,
            console: ColorfulConsole):
        self.switch = switch
        self.state = state
        self.backup = folder.joinpath("IDRecorder_backup.txt")
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

    def backup_file(self):
        if self.file and self.record:
            # print("Backup IDRecorder")  # 调试代码
            with self.backup.open("w", encoding=self.encode) as f:
                self.__save_file(f)

    def close(self):
        if self.file:
            self.__save_file(self.file)
            self.file.close()
            self.file = None
            # print("Close IDRecorder")  # 调试代码

    def __restore_data(self, ids: set) -> set:
        if self.state:
            return ids
        return set()
        self.console.print(
            f"程序检测到上次运行可能没有正常结束，您的作品下载记录数据可能已经丢失！\n数据文件路径：{self.path.resolve()}", style=ERROR)
        if self.backup.exists():
            if self.console.input(
                    "检测到 IDRecorder 备份文件，是否恢复最后一次备份的数据(YES/NO): ",
                    style=WARNING).upper() == "YES":
                self.path.write_text(
                    self.backup.read_text(
                        encoding=self.encode))
                self.console.print(
                    "IDRecorder 已恢复最后一次备份的数据，请重新运行程序！", style=INFO)
                return set(self.backup.read_text(encoding=self.encode).split())
            else:
                self.console.print(
                    "IDRecorder 数据未恢复，下载任意作品之后，备份数据会被覆盖导致无法恢复！", style=ERROR)
        else:
            self.console.print(
                "未检测到 IDRecorder 备份文件，您的作品下载记录数据无法恢复！",
                style=ERROR)
        return set()
