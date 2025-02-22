from typing_extensions import NamedTuple


class Info(NamedTuple):
    num: int
    file: str


class Line(str):
    def __new__(cls, value: str, num: int = 0, file: str = ""):
        obj = str.__new__(cls, value)
        obj.raw_data = value
        obj.num = num
        obj.file = file
        return obj

    def get_file_info(self) -> Info:
        return Info(
            num=self.num,
            file=self.file
        )

    def __str__(self) -> str:
        return f"Файл: '{self.file}', номер строки: '{self.num}', значение: '{self.raw_data}'"

    def __repr__(self):
        return f"{Line.__name__}(num={self.num}, value='{self}', file='{self.file}')"
