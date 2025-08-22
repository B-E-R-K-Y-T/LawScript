from typing import Any, Optional

from src.core.parse.base import Parser
from src.core.tokens import Tokens
from src.core.types.line import Line
from src.util.console_worker import printer


class SequenceMetadata:
    def __init__(self, seq: list):
        self.seq = seq


class DefineSequenceParser(Parser):
    def __init__(self):
        super().__init__()
        self.sequence: Optional[list[Any]] = None
        printer.logging("Инициализация DefineSequenceParser", level="INFO")

    def create_metadata(self) -> SequenceMetadata:
        if self.sequence is None:
            printer.logging("Попытка создания метаданных без инициализированной последовательности", level="ERROR")
            raise Exception("Sequence is not initialized")

        printer.logging(f"Создание метаданных с последовательностью: {self.sequence}", level="INFO")
        return SequenceMetadata(self.sequence)

    def parse(self, body: list[Line], jump: int) -> int:
        result = []
        printer.logging(f"Начало парсинга тела с jump={jump}", level="INFO")

        for word in body:
            word = (
                word.
                replace("[", "").
                replace("]", "").
                replace(Tokens.comma, "")
            )

            if not word:
                printer.logging("Пропускаем пустое слово", level="DEBUG")
                continue

            result.append(word)

        self.sequence = result
        printer.logging(f"Парсинг завершен. Обнаруженные слова: {self.sequence}", level="INFO")

        return jump
