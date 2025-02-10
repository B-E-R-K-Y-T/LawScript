from typing_extensions import NamedTuple


class Info(NamedTuple):
    num: int
    file: str


class Line(str):
    def __new__(cls, value: str, num: int = 0, file: str = ""):
        obj = str.__new__(cls, value)
        obj.num = num
        obj.file = file
        return obj

    def get_file_info(self) -> Info:
        return Info(
            num=self.num,
            file=self.file
        )

    def __repr__(self):
        return f"{Line.__name__}(num={self.num}, value='{self}', file='{self.file}')"
