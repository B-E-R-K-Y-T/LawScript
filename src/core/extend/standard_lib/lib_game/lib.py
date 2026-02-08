from typing import Optional

from pathlib import Path

from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/_/"
MOD_NAME = "game"


@builder.collect(func_name='_инициализация_игрового_движка')
class Init(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.types.atomic import VOID

        pygame.init()

        return VOID


@builder.collect(func_name='_создать_окно')
class CreateScreen(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 2

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.extend.standard_lib.lib_game.util import GameScreen
        from src.core.types.atomic import Number
        from src.core.exceptions import ErrorType

        wight = args[0]
        height = args[1]

        if not isinstance(wight, Number):
            raise ErrorType(f"Первый аргумент должен иметь тип '{Number.type_name()}'!")

        if not isinstance(height, Number):
            raise ErrorType(f"Второй аргумент должен иметь тип '{Number.type_name()}'!")

        screen = pygame.display.set_mode((wight.value, height.value))

        real_screen = GameScreen(screen)

        return real_screen


@builder.collect(func_name='_заголовок_окна')
class SetCaption(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.types.atomic import VOID, String
        from src.core.exceptions import ErrorType

        name = args[0]

        if not isinstance(name, String):
            raise ErrorType(f"Первый аргумент должен иметь тип '{String.type_name()}'!")

        pygame.display.set_caption(name.value)

        return VOID


@builder.collect(func_name='_получить_событие')
class GetEvent(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.extend.standard_lib.lib_game.util import GameEvent
        from src.core.types.atomic import Array

        events = []

        for event in pygame.event.get():
            events.append(GameEvent(event))

        return Array(events)


@builder.collect(func_name='_таблица_клавиш')
class KeyTable(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.types.atomic import Table, String, Number

        key_table = Table()

        # Добавляем основные коды клавиш
        keys = {
            "ВЛЕВО": pygame.K_LEFT,
            "ВПРАВО": pygame.K_RIGHT,
            "ВВЕРХ": pygame.K_UP,
            "ВНИЗ": pygame.K_DOWN,
            "ПРОБЕЛ": pygame.K_SPACE,
            "ENTER": pygame.K_RETURN,
            "ESC": pygame.K_ESCAPE,
            "SHIFT": pygame.K_LSHIFT,
            "CTRL": pygame.K_LCTRL,
            "ALT": pygame.K_LALT,
            "A": pygame.K_a,
            "D": pygame.K_d,
            "W": pygame.K_w,
            "S": pygame.K_s,
        }

        for key_name, key_code in keys.items():
            key_table.value[String(key_name)] = Number(key_code)

        return key_table


@builder.collect(func_name='_таблица_событий')
class EventTable(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.extend.standard_lib.lib_game.util import GameEventType
        from src.core.types.atomic import Table, String

        return Table({
            String("Выход"): GameEventType(pygame.QUIT),
            String("НажатиеКлавиши"): GameEventType(pygame.KEYDOWN),
            String("ОтпусканиеКлавиши"): GameEventType(pygame.KEYUP),
            String("НажатиеМыши"): GameEventType(pygame.MOUSEBUTTONDOWN),
            String("ОтпусканиеМыши"): GameEventType(pygame.MOUSEBUTTONUP),
            String("ДвижениеМыши"): GameEventType(pygame.MOUSEMOTION),
        })

@builder.collect(func_name='_заливка_окна')
class FillScreen(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 2

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.extend.standard_lib.lib_game.util import GameScreen
        from src.core.exceptions import ErrorType
        from src.core.types.atomic import Array, VOID

        screen, arr = args

        if not isinstance(screen, GameScreen):
            raise ErrorType(f"Первый аргумент должен иметь тип '{GameScreen.type_name()}'!")

        if not isinstance(arr, Array):
            raise ErrorType(f"Второй аргумент должен иметь тип '{Array.type_name()}'!")

        if len(arr.value) not in (3, 4):
            raise ErrorType(f"Цвет должен быть массивом из 3 (RGB) или 4 (RGBA) элементов!")

        _, parsed_arr = self.parse_args(args)

        try:
            color_tuple = tuple(parsed_arr)
        except (ValueError, TypeError):
            raise ErrorType("Все значения цвета должны быть целыми числами!")

        for val in color_tuple:
            if not 0 <= val <= 255:
                raise ErrorType(f"Значения цвета должны быть в диапазоне 0-255, получено: {val}")

        screen.screen.fill(color_tuple)

        return VOID


@builder.collect(func_name='_отобразить_картинку')
class BlitImageOnScreen(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 3

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.extend.standard_lib.lib_game.util import GameScreen, GameImage
        from src.core.exceptions import ErrorType
        from src.core.types.atomic import Array, VOID

        screen, image, arr = args

        if not isinstance(screen, GameScreen):
            raise ErrorType(f"Первый аргумент должен иметь тип '{GameScreen.type_name()}'!")

        if not isinstance(image, GameImage):
            raise ErrorType(f"Второй аргумент должен иметь тип '{GameImage.type_name()}'!")

        if not isinstance(arr, Array):
            raise ErrorType(f"Третий аргумент должен иметь тип '{Array.type_name()}'!")

        if len(arr.value) != 2:
            raise ErrorType(f"Количество координат в массиве должно быть равно 2-м (X и Y)")

        *_, parsed_arr = self.parse_args(args)

        try:
            cords_tuple = tuple(parsed_arr)
        except (ValueError, TypeError):
            raise ErrorType("Все значения цвета должны быть целыми числами!")

        screen.screen.blit(image.image, cords_tuple)

        return VOID


@builder.collect(func_name='_обновление_экрана')
class UpdateScreen(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.types.atomic import VOID

        pygame.display.flip()

        return VOID


@builder.collect(func_name='_загрузить_изображение')
class LoadImage(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.types.atomic import String
        from src.core.exceptions import ErrorType
        from src.core.extend.standard_lib.util import path_normpath
        from src.core.extend.standard_lib.lib_game.util import GameImage

        path_to_image = args[0]

        if not isinstance(path_to_image, String):
            raise ErrorType(f"Аргумент должен иметь тип '{String.type_name()}'!")

        return GameImage(pygame.image.load(path_normpath(path_to_image.value)))


@builder.collect(func_name='_выход_из_игры')
class GameExit(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.types.atomic import VOID

        pygame.quit()

        return VOID


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
