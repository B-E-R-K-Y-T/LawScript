import pygame

from src.core.types.atomic import CustomType, Number, Array, Boolean


class GameScreen(CustomType):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen

    def eq(self, other: 'GameScreen'):
        if isinstance(other, GameScreen):
            return self.screen == other.screen
        return False

    def __str__(self) -> str:
        return "ИгровоеОкно"

    @classmethod
    def type_name(cls):
        return "ИгровоеОкно"


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

    @classmethod
    def type_name(cls):
        return "ТипСобытия"


class GameEvent(CustomType):
    def __init__(self, event):
        super().__init__()
        self.event = event
        self.fields = {
            "тип": GameEventType(event.type),
            "это_выход": Boolean(self.event.type == pygame.QUIT)
        }

        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            self.fields["клавиша"] = Number(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
            self.fields["кнопка"] = Number(event.button)
            self.fields["позиция"] = Array([Number(event.pos[0]), Number(event.pos[1])])
        elif event.type == pygame.MOUSEMOTION:
            self.fields["позиция"] = Array([Number(event.pos[0]), Number(event.pos[1])])
            self.fields["относительно"] = Array([Number(event.rel[0]), Number(event.rel[1])])

    def eq(self, other: 'GameEvent'):
        if isinstance(other, GameEvent):
            return self.event == other.event
        return False

    def __str__(self) -> str:
        return "Событие"

    @classmethod
    def type_name(cls):
        return "Событие"


class GameImage(CustomType):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.fields = {
            "ширина": Number(image.get_width()),
            "высота": Number(image.get_height())
        }

    def eq(self, other: 'GameImage'):
        if isinstance(other, GameImage):
            return self.image == other.image
        return False

    def __str__(self) -> str:
        return "Картинка"

    @classmethod
    def type_name(cls):
        return "Картинка"


class GameRect(CustomType):
    def __init__(self, rect):
        super().__init__()
        self.rect = rect
        self.fields = {
            "x": Number(rect.x),
            "y": Number(rect.y),
            "ширина": Number(rect.width),
            "высота": Number(rect.height),
            "центр_x": Number(rect.centerx),
            "центр_y": Number(rect.centery),
            "верх": Number(rect.top),
            "низ": Number(rect.bottom),
            "лево": Number(rect.left),
            "право": Number(rect.right)
        }

    def eq(self, other: 'GameRect'):
        if isinstance(other, GameRect):
            return self.rect == other.rect
        return False

    def __str__(self) -> str:
        return "Прямоугольник"

    @classmethod
    def type_name(cls):
        return "Прямоугольник"


class GameText(CustomType):
    def __init__(self, text_surface):
        super().__init__()
        self.text_surface = text_surface
        self.fields = {
            "ширина": Number(text_surface.get_width()),
            "высота": Number(text_surface.get_height())
        }

    def eq(self, other: 'GameText'):
        if isinstance(other, GameText):
            return self.text_surface == other.text_surface
        return False

    def __str__(self) -> str:
        return "Текст"

    @classmethod
    def type_name(cls):
        return "Текст"
