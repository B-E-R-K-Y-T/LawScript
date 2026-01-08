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
