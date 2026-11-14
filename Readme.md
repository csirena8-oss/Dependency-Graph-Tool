# Dependency Graph Tool — вариант №25 (этапы 1–2)

## Содержание

1. [Общее описание](#1-общее-описание)
2. [Область применения и ограничения задания](#2-область-применения-и-ограничения-задания)
3. [Требования](#3-требования)
4. [Структура репозитория](#4-структура-репозитория)
5. [Быстрый старт](#5-быстрый-старт)
6. [Настраиваемые параметры](#6-настраиваемые-параметры)
7. [Описание функций и модулей](#7-описание-функций-и-модулей)
8. [Сборка проекта](#8-сборка-проекта)
9. [Запуск тестов](#9-запуск-тестов)
10. [Примеры использования](#10-примеры-использования)
11. [Обработка ошибок](#11-обработка-ошибок)

---

## 1. Общее описание

`Dependency Graph Tool` — это консольное (CLI) приложение на Python 3,
предназначенное для анализа зависимостей пакетов формата
**Ubuntu (apt)**.

Данный репозиторий реализует **только этапы 1 и 2** варианта №25
из сборника практических работ №2 по дисциплине
«Конфигурационное управление»:

- **Этап 1** — минимальный прототип CLI-приложения с конфигурацией.
  Источником параметров являются **опции командной строки**.
  При запуске выводятся все настраиваемые пользователем параметры
  в формате `ключ=значение`. Для каждого параметра реализована
  и продемонстрирована обработка ошибок.
- **Этап 2** — сбор данных. Из индекса Ubuntu `Packages`
  (plain/`.gz`/`.xz`) извлекается информация о **прямых**
  зависимостях заданного пакета **указанной пользователем версии**.
  Готовые менеджеры пакетов (apt, apt-get, aptitude, dpkg)
  и сторонние библиотеки для получения зависимостей
  **не используются** — только стандартная библиотека Python.

Программа не строит граф транзитивных зависимостей и не выполняет
визуализацию — это задачи этапов 3–5, которые в данной реализации
намеренно не выполнялись.

---

## 2. Область применения и ограничения задания

Согласно варианту №25:

| Параметр варианта                | Значение                          |
| -------------------------------- | --------------------------------- |
| Источник параметров              | опции командной строки            |
| Формат пакетов                   | Ubuntu (apt)                      |
| Получение данных о версии пакета | обязательно (по версии из `--version`) |
| Этап 1                           | реализован                        |
| Этап 2                           | реализован                        |
| Этапы 3–5                        | не реализованы                    |

Запрещено использовать:

- `apt`, `apt-get`, `aptitude`, `dpkg`, `apt-cache`, `apt-rdepends`;
- сторонние библиотеки Python для работы с `Packages`-индексом;
- готовые библиотеки для построения графов зависимостей.

Разрешено и используется:

- `urllib.request` — загрузка индекса по HTTP(S);
- `gzip`, `lzma` — распаковка `.gz` и `.xz`;
- `argparse` — разбор опций командной строки;
- `dataclasses`, `pathlib`, `re`, `unittest` — стандартная библиотека.

---

## 3. Требования

- **Python**: 3.10 или выше (используются `list[str]`, `dict[str, str]`
  и union-типы `X | None`).
- **ОС**: Linux, macOS или Windows (любая, где доступен Python 3.10+).
- **Сеть**: нужна только для удалённого режима (`--repo` указывает
  на URL). В тестовом режиме (`--test-mode`) сеть не требуется.
- **Внешние зависимости**: отсутствуют. `pip install` не нужен.

Проверить версию Python:

```bash
python3 --version
```

---

## 4. Структура репозитория

```text
.
├── .gitignore
├── README.md
├── Makefile
├── run.sh
├── src
│   ├── __init__.py
│   ├── apt_index.py
│   ├── cli.py
│   └── config.py
└── tests
    ├── __init__.py
    ├── fixtures
    │   └── Packages
    ├── test_apt_index.py
    └── test_config.py
```

| Путь                    | Назначение                                                   |
| ----------------------- | ------------------------------------------------------------ |
| `src/`                  | Исходный код                                                 |
| `src/cli.py`            | Точка входа CLI, разбор аргументов, диспетчеризация этапов   |
| `src/config.py`         | Модель конфигурации и валидация всех параметров              |
| `src/apt_index.py`      | Чтение и разбор `Packages`-индекса, извлечение зависимостей  |
| `tests/`                | Юнит-тесты (`unittest`)                                      |
| `tests/fixtures/`       | Тестовый apt-индекс для этапа 2                              |
| `run.sh`                | Скрипт запуска CLI                                           |
| `Makefile`              | Команда `make test` для запуска тестов                       |
| `.gitignore`            | Исключения для артефактов сборки, кешей и служебных файлов   |

---

## 5. Быстрый старт

```bash
# 1. Перейти в каталог репозитория
cd dependency-graph-tool

# 2. Сделать run.sh исполняемым (один раз)
chmod +x run.sh

# 3. Прогнать тесты
make test

# 4. Запустить пример этапа 1
./run.sh --stage 1 \
  --package app \
  --repo tests/fixtures/Packages \
  --test-mode \
  --version 1.0 \
  --max-depth 3

# 5. Запустить пример этапа 2
./run.sh --stage 2 \
  --package app \
  --repo tests/fixtures/Packages \
  --test-mode \
  --version 1.0 \
  --max-depth 3
```

---

## 6. Настраиваемые параметры

Все параметры задаются **опциями командной строки**. Парсер построен
на `argparse`.

| Опция          | Тип        | Обязательно | Значение по умолчанию | Описание                                                                 |
| -------------- | ---------- | :---------: | :-------------------: | ------------------------------------------------------------------------ |
| `--package`    | `str`      |     да      |          —            | Имя анализируемого пакета (формат имени Debian-пакета)                   |
| `--repo`       | `str`      |     да      |          —            | URL индекса репозитория или путь к локальному файлу `Packages`           |
| `--version`    | `str`      |     да      |          —            | Версия пакета, для которой запрашиваются зависимости                     |
| `--max-depth`  | `int`      |     да      |          —            | Максимальная глубина анализа зависимостей (целое ≥ 1)                    |
| `--test-mode`  | флаг       |    нет      |        `false`        | Режим тестирования: `--repo` трактуется как путь к локальному файлу      |
| `--stage`      | `int`      |    нет      |         `1`           | Этап: `1` — вывод конфигурации, `2` — вывод прямых зависимостей         |

### 6.1 Правила валидации

- **`--package`**: должен соответствовать регулярному выражению
  `^[a-z0-9][a-z0-9+.-]*$` (имя Debian-пакета в нижнем регистре).
  Пустая строка, пробелы, заглавные буквы и прочие символы — ошибка.
- **`--version`**: непустая строка без пробельных символов.
- **`--max-depth`**: целое число `≥ 1`. `0` и отрицательные значения
  отклоняются.
- **`--repo`**:
  - в тестовом режиме (`--test-mode`): должен указывать на существующий
    локальный файл;
  - в удалённом режиме: должен быть корректным `http`/`https`-URL
    с непустым хостом.
- **`--stage`**: допускается только `1` или `2`.

### 6.2 Вывод на этапе 1

На этапе 1 программа выводит все параметры в формате `ключ=значение`:

```text
package=app
repo=tests/fixtures/Packages
test_mode=true
version=1.0
max_depth=3
```

### 6.3 Вывод на этапе 2

На этапе 2 программа выводит прямые зависимости заданного пакета,
**по одной на строку**, без дубликатов, в порядке появления
в поле `Depends` (с учётом альтернатив и квалификаторов):

```text
liba
libb
libd
```

Правила извлечения имён из `Depends`:

- альтернативы через `|` — берётся **первая** (левая) альтернатива;
- квалификатор версии `(>= 1.0)` и `(:any)`/`(:arch)` — отбрасывается;
- пробелы вокруг имён — обрезаются;
- дубликаты в результирующем списке устраняются (с сохранением
  порядка).

---

## 7. Описание функций и модулей

### 7.1 `src/config.py`

Модуль описывает модель конфигурации и её валидацию.

#### `class Config`

`@dataclass(frozen=True)` — неизменяемая модель конфигурации.

| Поле         | Тип    | Описание                                  |
| ------------ | ------ | ----------------------------------------- |
| `package`    | `str`  | Имя пакета                                |
| `repo`       | `str`  | URL индекса или путь к локальному файлу   |
| `test_mode`  | `bool` | Признак тестового режима                  |
| `version`    | `str`  | Версия пакета                             |
| `max_depth`  | `int`  | Максимальная глубина анализа              |

#### `class ConfigError(ValueError)`

Исключение, возникающее при неверных параметрах.

#### `validate_config(config: Config) -> None`

Проверяет все параметры конфигурации. Возбуждает `ConfigError` при
первой найденной ошибке. Внутри вызывает приватные проверки
`_validate_package`, `_validate_version`, `_validate_depth`,
`_validate_repo`.

**Пример:**

```python
from src.config import Config, ConfigError, validate_config

cfg = Config(
    package="app",
    repo="tests/fixtures/Packages",
    test_mode=True,
    version="1.0",
    max_depth=3,
)
try:
    validate_config(cfg)
except ConfigError as exc:
    print("Ошибка конфигурации:", exc)
```

### 7.2 `src/apt_index.py`

Модуль чтения apt-индекса и извлечения зависимостей.

#### `class AptIndexError(ValueError)`

Исключение, возникающее при ошибках чтения/разбора индекса
или при отсутствии пакета нужной версии.

#### `read_index(location: str, test_mode: bool) -> str`

Читает индекс `Packages` из локального файла или по URL и возвращает
его как строку.

- В `test_mode=True` читает файл по `location`.
- Иначе пробует по очереди `Packages`, `Packages.gz`, `Packages.xz`
  относительно `location` (см. `candidate_urls`).
- Поддерживает форматы: plain, `.gz`, `.xz` (определяются по магическим
  байтам).

**Исключения:** `AptIndexError`, `OSError`, `URLError`.

#### `candidate_urls(url: str) -> list[str]`

Возвращает список URL-кандидатов для чтения индекса:

- если `url` уже заканчивается на `Packages`, `Packages.gz`
  или `Packages.xz` — возвращает `[url]`;
- иначе формирует `<url>/Packages`, `<url>/Packages.gz`,
  `<url>/Packages.xz`.

#### `decode_index(data: bytes, name: str) -> str`

Декодирует данные индекса, автоматически распознавая gzip и xz
по магическим байтам:

- `\x1f\x8b` — gzip;
- `\xfd7zXZ\x00` — xz;
- иначе — plain UTF-8.

#### `parse_stanzas(text: str) -> list[dict[str, str]]`

Разбирает текст индекса на «стансы» — блоки между пустыми строками.
Строки продолжения (начинающиеся с пробела/табуляции) присоединяются
к предыдущему полю. Возвращает список словарей.

#### `parse_depends(value: str) -> list[str]`

Извлекает имена зависимостей из поля `Depends`.

**Пример:**

```python
from src.apt_index import parse_depends

parse_depends("liba (>= 1.0), libb | libc, libd:any")
# ['liba', 'libb', 'libd']
```

#### `find_package(stanzas, name, version) -> dict[str, str]`

Ищет станс пакета с совпадением `Package == name` и
`Version == version`. Возбуждает `AptIndexError`, если пакет
не найден.

#### `direct_dependencies(text, name, version) -> list[str]`

Высокоуровневая функция:

1. Разбирает `text` в стансы через `parse_stanzas`.
2. Находит станс через `find_package`.
3. Извлекает прямые зависимости через `parse_depends`.

**Пример:**

```python
from src.apt_index import direct_dependencies

text = open("tests/fixtures/Packages").read()
print(direct_dependencies(text, "app", "1.0"))
# ['liba', 'libb', 'libd']
```

### 7.3 `src/cli.py`

Модуль CLI.

#### `build_parser() -> argparse.ArgumentParser`

Создаёт и возвращает `argparse.ArgumentParser` со всеми опциями
из раздела 6.

#### `config_from_args(args: argparse.Namespace) -> Config`

Преобразует `argparse.Namespace` в `Config`.

#### `print_config(config: Config) -> None`

Печатает конфигурацию на этапе 1 в формате `ключ=значение`.

#### `run_stage_two(config: Config) -> None`

Читает индекс через `read_index`, вызывает `direct_dependencies`
и печатает каждую зависимость на отдельной строке.

#### `main(argv: list[str] | None = None) -> int`

Точка входа CLI. Возвращает:

- `0` — успех;
- `2` — ошибка конфигурации, чтения индекса или ОС.

Все ошибки перехватываются и печатаются в `stderr` в формате
`error: <сообщение>`.

---

## 8. Сборка проекта

Проект **не требует сборки**: это чистый Python без компиляции.
Тем не менее предусмотрены скрипты для запуска.

### 8.1 Подготовка

```bash
chmod +x run.sh
```

### 8.2 Запуск

```bash
./run.sh --help
```

или эквивалентно:

```bash
python3 -m src.cli --help
```

### 8.3 Скрипт `run.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

python3 -m src.cli "$@"
```

`set -euo pipefail` обеспечивает остановку при первой ошибке,
запрет неинициализированных переменных и корректную обработку пайпов.

---

## 9. Запуск тестов

Тесты реализованы через `unittest` и лежат в `tests/`.

### 9.1 Через `make`

```bash
make test
```

Соответствующая цель Makefile:

```makefile
.PHONY: test

test:
	python3 -m unittest discover -s tests -v
```

### 9.2 Напрямую

```bash
python3 -m unittest discover -s tests -v
```

### 9.3 Отдельные модули тестов

```bash
python3 -m unittest tests.test_config -v
python3 -m unittest tests.test_apt_index -v
```

### 9.4 Что покрыто тестами

`tests/test_config.py`:

- корректная удалённая конфигурация;
- неверное имя пакета (пробелы, заглавные буквы);
- неверная версия (пробелы в версии);
- неверная глубина (`0`);
- неверный URL (не `http`/`https`);
- отсутствующий файл в тестовом режиме;
- корректный файл в тестовом режиме.

`tests/test_apt_index.py`:

- `parse_depends` на сложной строке с альтернативами и версиями;
- `parse_depends` на пустой строке;
- `parse_stanzas` на фикстуре (4 станса);
- `direct_dependencies` для `app@1.0` → `['liba', 'libb', 'libd']`;
- отсутствие пакета → `AptIndexError`.

Ожидаемо все тесты проходят на чистом Python 3.10+.

---

## 10. Примеры использования

### 10.1 Этап 1: вывод конфигурации (тестовый файл)

```bash
./run.sh --stage 1 \
  --package app \
  --repo tests/fixtures/Packages \
  --test-mode \
  --version 1.0 \
  --max-depth 3
```

Вывод:

```text
package=app
repo=tests/fixtures/Packages
test_mode=true
version=1.0
max_depth=3
```

### 10.2 Этап 1: вывод конфигурации (удалённый репозиторий)

```bash
./run.sh --stage 1 \
  --package curl \
  --repo https://example.com/ubuntu/dists/jammy/main/binary-amd64/ \
  --version 8.5.0-2ubuntu10 \
  --max-depth 3
```

Вывод:

```text
package=curl
repo=https://example.com/ubuntu/dists/jammy/main/binary-amd64/
test_mode=false
version=8.5.0-2ubuntu10
max_depth=3
```

### 10.3 Этап 2: прямые зависимости из локального индекса

```bash
./run.sh --stage 2 \
  --package app \
  --repo tests/fixtures/Packages \
  --test-mode \
  --version 1.0 \
  --max-depth 3
```

Вывод:

```text
liba
libb
libd
```

### 10.4 Этап 2: прямые зависимости из удалённого индекса

`--repo` может быть как прямым URL на `Packages`/`Packages.gz`/
`Packages.xz`, так и базовым URL, рядом с которым лежат эти файлы.

Прямой URL:

```bash
./run.sh --stage 2 \
  --package curl \
  --repo https://example.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz \
  --version 8.5.0-2ubuntu10 \
  --max-depth 3
```

Базовый URL (программа попробует `Packages`, `Packages.gz`,
`Packages.xz`):

```bash
./run.sh --stage 2 \
  --package curl \
  --repo https://example.com/ubuntu/dists/jammy/main/binary-amd64/ \
  --version 8.5.0-2ubuntu10 \
  --max-depth 3
```

Вывод (примерный):

```text
libc6
libcurl4
zlib1g
```

### 10.5 Негативные сценарии

Неверное имя пакета:

```bash
./run.sh --stage 1 \
  --package "Bad Name" \
  --repo https://example.com/Packages.gz \
  --version 1.0 \
  --max-depth 3
# error: package must match Debian package name format
# код возврата: 2
```

Неверная глубина:

```bash
./run.sh --stage 1 \
  --package app \
  --repo https://example.com/Packages.gz \
  --version 1.0 \
  --max-depth 0
# error: max-depth must be a positive integer
```

Отсутствующий файл в тестовом режиме:

```bash
./run.sh --stage 2 \
  --package app \
  --repo missing.file \
  --test-mode \
  --version 1.0 \
  --max-depth 3
# error: test repository file not found
```

Неверный URL:

```bash
./run.sh --stage 1 \
  --package app \
  --repo ftp://example.com/Packages \
  --version 1.0 \
  --max-depth 3
# error: repo must be an http(s) URL or a test file path
```

Пакет не найден:

```bash
./run.sh --stage 2 \
  --package missing \
  --repo tests/fixtures/Packages \
  --test-mode \
  --version 1.0 \
  --max-depth 3
# error: package missing version 1.0 not found
```

Неверный этап:

```bash
./run.sh --stage 3 \
  --package app \
  --repo tests/fixtures/Packages \
  --test-mode \
  --version 1.0 \
  --max-depth 3
# argparse: invalid choice: 3 (choose from 1, 2)
# код возврата: 2
```

### 10.6 Помощь по CLI

```bash
./run.sh --help
```

Вывод — автоматически сгенерированное описание всех опций.

---

## 11. Обработка ошибок

| Ситуация                                   | Исключение / поведение                      | Код возврата |
| ------------------------------------------ | ------------------------------------------- | :----------: |
| Неверное имя пакета                        | `ConfigError`                               |      2       |
| Пустая или «с пробелами» версия            | `ConfigError`                               |      2       |
| `--max-depth` ≤ 0                          | `ConfigError`                               |      2       |
| Неверный URL (не `http`/`https`)           | `ConfigError`                               |      2       |
| Нет файла в тестовом режиме                | `ConfigError`                               |      2       |
| Индекс недоступен / не найден              | `AptIndexError`, `OSError`, `URLError`      |      2       |
| Индекс не декодируется                     | `AptIndexError`                             |      2       |
| Пакет нужной версии не найден              | `AptIndexError`                             |      2       |
| Неверный `--stage`                         | `argparse` (выбор из `{1, 2}`)              |      2       |
| Успех                                      | —                                           |      0       |

Все сообщения об ошибках печатаются в `stderr` в формате
`error: <сообщение>`. Это позволяет отделить диагностику от полезного
вывода (прямых зависимостей) и использовать программу в скриптах.