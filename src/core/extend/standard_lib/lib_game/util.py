from src.core.types.atomic import CustomType


class GameScreen(CustomType):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen


class GameEventType(CustomType):
    def __init__(self, type_):
        super().__init__(type_)
        self.type = type_

    def eq(self, other: 'GameEventType'):
        if isinstance(other, GameEventType):
            return self.type == other.type

        return False

    def __str__(self) -> str:
        return str(self.value)


class GameEvent(CustomType):
    def __init__(self, event):
        super().__init__()
        self.event = event
        self.fields = {
            "тип": GameEventType(event.type)
        }

    def eq(self, other: 'GameEvent'):
        if isinstance(other, GameEvent):
            return self.event == other.event

        return False

    def __str__(self) -> str:
        return "Событие"


class GameImage(CustomType):
    def __init__(self, image):
        super().__init__()
        self.image = image

    def eq(self, other: 'GameImage'):
        if isinstance(other, GameImage):
            return self.image == other.image

        return False

    def __str__(self) -> str:
        return "Картинка"
