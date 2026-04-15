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


@builder.collect(func_name='_задержка')
class Delay(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.types.atomic import Number, VOID
        from src.core.exceptions import ErrorType

        milliseconds = args[0]

        if not isinstance(milliseconds, Number):
            raise ErrorType(f"Аргумент должен иметь тип '{Number.type_name()}'!")

        pygame.time.delay(int(milliseconds.value))

        return VOID


@builder.collect(func_name='_получить_время')
class GetTicks(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.types.atomic import Number

        return Number(pygame.time.get_ticks())


@builder.collect(func_name='_получить_позицию_мыши')
class GetMousePos(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.types.atomic import Array, Number

        pos = pygame.mouse.get_pos()

        return Array([Number(pos[0]), Number(pos[1])])


@builder.collect(func_name='_нажата_ли_клавиша')
class IsKeyPressed(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.types.atomic import Number, Boolean
        from src.core.exceptions import ErrorType

        key_code = args[0]

        if not isinstance(key_code, Number):
            raise ErrorType(f"Аргумент должен иметь тип '{Number.type_name()}'!")

        keys = pygame.key.get_pressed()
        result = keys[int(key_code.value)]

        return Boolean(result)


@builder.collect(func_name='_нажата_ли_кнопка_мыши')
class IsMouseButtonPressed(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.types.atomic import Number, Boolean
        from src.core.exceptions import ErrorType

        button = args[0]

        if not isinstance(button, Number):
            raise ErrorType(f"Аргумент должен иметь тип '{Number.type_name()}'!")

        buttons = pygame.mouse.get_pressed()
        button_index = int(button.value) - 1

        if button_index < 0 or button_index >= len(buttons):
            raise ErrorType("Номер кнопки мыши должен быть 1, 2 или 3!")

        return Boolean(buttons[button_index])


@builder.collect(func_name='_создать_прямоугольник')
class CreateRect(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 4

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.extend.standard_lib.lib_game.util import GameRect
        from src.core.types.atomic import Number
        from src.core.exceptions import ErrorType

        x, y, width, height = args

        for i, arg in enumerate([x, y, width, height]):
            if not isinstance(arg, Number):
                raise ErrorType(f"Аргумент {i + 1} должен иметь тип '{Number.type_name()}'!")

        rect = pygame.Rect(
            int(x.value),
            int(y.value),
            int(width.value),
            int(height.value)
        )

        return GameRect(rect)


@builder.collect(func_name='_нарисовать_прямоугольник')
class DrawRect(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 4

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.extend.standard_lib.lib_game.util import GameScreen, GameRect
        from src.core.types.atomic import Array, Number, VOID
        from src.core.exceptions import ErrorType

        screen, rect, color_arr, width = args

        if not isinstance(screen, GameScreen):
            raise ErrorType(f"Первый аргумент должен иметь тип '{GameScreen.type_name()}'!")

        if not isinstance(rect, GameRect):
            raise ErrorType(f"Второй аргумент должен иметь тип '{GameRect.type_name()}'!")

        if not isinstance(color_arr, Array):
            raise ErrorType(f"Третий аргумент должен иметь тип '{Array.type_name()}'!")

        if not isinstance(width, Number):
            raise ErrorType(f"Четвёртый аргумент должен иметь тип '{Number.type_name()}'!")

        if len(color_arr.value) != 3:
            raise ErrorType("Цвет должен быть массивом из 3 элементов (RGB)!")

        *_, parsed_color, parsed_width = self.parse_args(args)

        try:
            color_tuple = tuple(parsed_color)
        except (ValueError, TypeError):
            raise ErrorType("Все значения цвета должны быть целыми числами!")

        pygame.draw.rect(
            screen.screen,
            color_tuple,
            rect.rect,
            int(parsed_width)
        )

        return VOID


@builder.collect(func_name='_нарисовать_круг')
class DrawCircle(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 5

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.extend.standard_lib.lib_game.util import GameScreen
        from src.core.types.atomic import Array, Number, VOID
        from src.core.exceptions import ErrorType

        screen, color_arr, x, y, radius = args

        if not isinstance(screen, GameScreen):
            raise ErrorType(f"Первый аргумент должен иметь тип '{GameScreen.type_name()}'!")

        if not isinstance(color_arr, Array):
            raise ErrorType(f"Второй аргумент должен иметь тип '{Array.type_name()}'!")

        for i, arg in enumerate([x, y, radius], 3):
            if not isinstance(arg, Number):
                raise ErrorType(f"Аргумент {i} должен иметь тип '{Number.type_name()}'!")

        if len(color_arr.value) != 3:
            raise ErrorType("Цвет должен быть массивом из 3 элементов (RGB)!")

        *_, parsed_color, parsed_x, parsed_y, parsed_radius = self.parse_args(args)

        try:
            color_tuple = tuple(parsed_color)
        except (ValueError, TypeError):
            raise ErrorType("Все значения цвета должны быть целыми числами!")

        pygame.draw.circle(
            screen.screen,
            color_tuple,
            (int(parsed_x), int(parsed_y)),
            int(parsed_radius)
        )

        return VOID


@builder.collect(func_name='_нарисовать_линию')
class DrawLine(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 6

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.extend.standard_lib.lib_game.util import GameScreen
        from src.core.types.atomic import Array, Number, VOID
        from src.core.exceptions import ErrorType

        screen, color_arr, x1, y1, x2, y2 = args

        if not isinstance(screen, GameScreen):
            raise ErrorType(f"Первый аргумент должен иметь тип '{GameScreen.type_name()}'!")

        if not isinstance(color_arr, Array):
            raise ErrorType(f"Второй аргумент должен иметь тип '{Array.type_name()}'!")

        for i, arg in enumerate([x1, y1, x2, y2], 3):
            if not isinstance(arg, Number):
                raise ErrorType(f"Аргумент {i} должен иметь тип '{Number.type_name()}'!")

        if len(color_arr.value) != 3:
            raise ErrorType("Цвет должен быть массивом из 3 элементов (RGB)!")

        *_, parsed_color, parsed_x1, parsed_y1, parsed_x2, parsed_y2 = self.parse_args(args)

        try:
            color_tuple = tuple(parsed_color)
        except (ValueError, TypeError):
            raise ErrorType("Все значения цвета должны быть целыми числами!")

        pygame.draw.line(
            screen.screen,
            color_tuple,
            (int(parsed_x1), int(parsed_y1)),
            (int(parsed_x2), int(parsed_y2))
        )

        return VOID


@builder.collect(func_name='_создать_текст')
class CreateText(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 3

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import pygame

        from src.core.extend.standard_lib.lib_game.util import GameText
        from src.core.types.atomic import String, Number, Array
        from src.core.exceptions import ErrorType

        text, size, color_arr = args

        if not isinstance(text, String):
            raise ErrorType(f"Первый аргумент должен иметь тип '{String.type_name()}'!")

        if not isinstance(size, Number):
            raise ErrorType(f"Второй аргумент должен иметь тип '{Number.type_name()}'!")

        if not isinstance(color_arr, Array):
            raise ErrorType(f"Третий аргумент должен иметь тип '{Array.type_name()}'!")

        if len(color_arr.value) != 3:
            raise ErrorType("Цвет должен быть массивом из 3 элементов (RGB)!")

        *_, parsed_size, parsed_color = self.parse_args(args)

        try:
            color_tuple = tuple(parsed_color)
        except (ValueError, TypeError):
            raise ErrorType("Все значения цвета должны быть целыми числами!")

        font = pygame.font.Font(None, int(parsed_size))
        text_surface = font.render(text.value, True, color_tuple)

        return GameText(text_surface)


@builder.collect(func_name='_отобразить_текст')
class BlitText(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 4

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.extend.standard_lib.lib_game.util import GameScreen, GameText
        from src.core.types.atomic import Number, VOID
        from src.core.exceptions import ErrorType

        screen, text_obj, x, y = args

        if not isinstance(screen, GameScreen):
            raise ErrorType(f"Первый аргумент должен иметь тип '{GameScreen.type_name()}'!")

        if not isinstance(text_obj, GameText):
            raise ErrorType(f"Второй аргумент должен иметь тип '{GameText.type_name()}'!")

        for i, arg in enumerate([x, y], 3):
            if not isinstance(arg, Number):
                raise ErrorType(f"Аргумент {i} должен иметь тип '{Number.type_name()}'!")

        *_, parsed_x, parsed_y = self.parse_args(args)

        screen.screen.blit(text_obj.text_surface, (int(parsed_x), int(parsed_y)))

        return VOID


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
