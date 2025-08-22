from typing import Optional

from src.core.types.basetype import BaseType


class Docs(BaseType):
    def __init__(self, name: str, docs_text: Optional[str] = None):
        super().__init__(name)
        self.docs_text = docs_text

    def __repr__(self) -> str:
        return f"Docs(docs_text={self.docs_text})"

