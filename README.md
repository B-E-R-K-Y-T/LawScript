# Язык написания контрактов: LawScript!

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/B-E-R-K-Y-T/LawScript)

## Сырой запуск:


### Windows
```
py -m venv .venv 
.venv/Scripts/activate
set PYTHONPATH=%CD%
pip install -r requirements.txt
py law.py --run hello_world.raw
```

### Linux/Mac

#### ВАЖНО! На маке могут потребоваться "танцы с бубном!"

```
py -m venv .venv 
.venv/Scripts/activate
export PYTHONPATH=$(pwd)
pip install -r requirements.txt
py law.py --run hello_world.raw
```

## Сборка:

```
pyinstaller --onefile --add-data="src;src" --hidden-import=requests .\law.py
```

### Запуск exe

```
law.exe --run hello_world.raw
```

Если Вы увидете такой вывод: 

![img.png](docs/img_6.png)

Значит LawScript работает штатно!

### Конфигурация

Для настройки LawScript создайте файл law_config.env

### Философия языка

Данный язык совмещает в себе две философии: Декларативную и Императивную


## Пример императивного кода

1
![img1.png](docs/img1.png)

2
![img3.png](docs/img3.png)

3
![img.png](docs/img4.png)

## Пример декларативного кода

![img.png](docs/img.png)


## Пример обработки ошибок

----
Язык понимает, что вы имели в виду, даже когда вы ошибаетесь!
![img.png](docs/img5.png)
![img.png](docs/img7.png)

----
Не переданные аргументы
![img.png](docs/img8.png)
![img.png](docs/img9.png)

----
Одинаковые аргументы
![img.png](docs/img10.png)
![img.png](docs/img11.png)

----
Двойное ожидание фоновой задачи
![img.png](docs/img12.png)
![img.png](docs/img13.png)

----
Хорошо понимает контекст ошибки. Показывает конкретное выражение
![img.png](docs/img14.png)
![img.png](docs/img15.png)

----
В рамках выражений, тоже хорошо понимает, что сломалось
![img.png](docs/img16.png)
![img.png](docs/img17.png)