## Домашнее задание 01 - Анализатор логов

*Задание*: Реализовать анализатор логов веб-сервиса в новом проекте, засетапленном по всем лучшим практикам

#### Требуемая функциональность:
1. Скрипт обрабатывает при запуске последний (со самой свежей датой в имени, не по mtime файла!) лог в `LOG_DIR`, в результате работы должен получится отчет как в `report-2017.06.30.html` (для корректной работы нужно будет найти и принести себе на диск `jquery.tablesorter.min.js`). То есть скрипт читает лог, парсит нужные поля, считает необходимую статистику по url'ам и рендерит шаблон `report.html` (в шаблоне нужно только подставить `$table_json`) в `report-YYYY.MM.DD.html`, где дата в названии соответствует дате обработанного файла логов . Ситуация, что логов на обработку нет возможна, это не должно являться ошибкой;
2. Готовые отчеты лежат в `REPORT_DIR`. В отчет попадает `REPORT_SIZE` URL'ов с наибольшим суммарным временем обработки (`time_sum`);
3. Скрипту должно быть возможно указать считать конфиг из другого файла, передав его путь через `--config`. У пути конфига должно быть дефолтное значение. Если файл не существует или не парсится, нужно выходить с ошибкой;
4. В переменной `config` находится конфиг по умолчанию. В конфиге, считанном из файла, могут быть переопределены перменные дефолтного конфига (некоторые, все или никакие, т.е. файл может быть пустой) и они имеют более высокий приоритет по сравнению с дефолтным конфигом. Таким образом, результирующий конфиг получается слиянием конфига из файла и дефолтного, с приоритетом конфига из файла. Ситуацию, когда конфига на диске не оказалось, нужно исключить;
5. Использовать конфиг как глобальную переменную запрещено, т.е. обращаться в своем функционале к нему так, как будто он глобальный - нельзя. Нужно передавать как аргумент;
6. Использовать сторонние библиотеки для реализации основного функционала запрещено, за исключение `structlog`;
7. (задание со "звездочкой") Если скрипт удачно обработал, то работу не переделывает при повторном запуске.


#### Требования к мониторингу в анализаторе:
1. Cкрипт должен писать структурированные логи в JSON через [structlog](https://www.structlog.org/en/stable/why.html) (плюс, рекомендуется познакомиться с утилитой [jq](https://jqlang.github.io/jq/)). Допускается только использование уровней `debug`, `info`, `error`. Путь до логфайла указывается в конфиге, если не указан, лог должен писаться в stdout;
2. все возможные "неожиданные" ошибки должны попадать в лог вместе с трейсбеком. Имеются в виду ошибки непредусмотренные логикой работы, приводящие к остановке обработки и выходу: баги, нажатие ctrl+C, кончилось место на диске и т.п.

#### Требования к тестированию:

На скрипт должны быть написаны тесты с использованием библиотеки `pytest`. Тестируемые кейсы и структура тестов определяется самостоятельно.

#### Требования к оформлению:
1. Задать проекту типовую структуру (можно ориентироваться https://realpython.com/python-application-layouts/ или свои любимые крупные проекты на github);
2. Настроить pre-commit хуки, как минимум линтер, black, isort, mypy и poetry;
3. Настроить CI со стандартными проверками: линтер, black, isort, mypy, - и запуском тестов;
4. Написать README.md с его кратким описанием и примерами запуска;
5. Настройку и управление зависимостями провести через poetry и pyproject.toml (ну и возможно setup.cfg);
6. Подготовить Makefile для удобного запуска линтовки, тестов (и тестового покрытия) и самого приложения.

___________
##  Реализация:

### 1. Анализатор логов:
#### 1.1 Файл конфигурации:
Файл конфигурации анализатора лога имеет следующий вид.
```ini
[INIT]
REPORT_SIZE = 1000
REPORT_DIR = reports
LOG_DIR = log
LOG_FILE = my_log_0001.log
```
С помощью указанных параметров задаются условия работы программы. В случае отсутствия одного из значений - будет использован параметр по умолчанию.
Также, при помощи ключа "--config" может быть задан любой другой файл конфигурацией, но с аналогичной внутренней структурой.

#### 1.2 Запуск анализатора:
Запуск анализатора может быть выполнен при помощи двух команд:
```bash
python3 main.py
```
```bash
make run
```
При наличии файла лога с последней, для которого отсуствует соотвествующий report - вы полняется анализ и генерация отчета. Если файлу лога соотвествует файл отчета с той же датой - повторная работа не выполняется.
```
Logger start with cfg LOG=my_log_0001.log
{"level": "info", "timestamp": "2025-04-26 18:36:03", "msg": "Last log is log/nginx-access-ui.log-20250130.gz"}
.gz
{"level": "info", "timestamp": "2025-04-26 18:36:03", "msg": "Get log in zip type..."}
{"report_name": "reports/report-2025.01.30.html", "level": "info", "timestamp": "2025-04-26 18:36:10", "msg": "Report success created!"}
```
Логи реализованы через structlog и пишутся в файл, если соответсвующий параметр есть в файле конфигурации, а так же выводятся в stdout.

#### 1.3 Тесторование:
В рамках задачи реализовано демонстрационное тестирование логики работы. Тестирование может быть запущено посредством команды ```poetry run pytest -v .```
Получаем результат:
```
platform linux -- Python 3.12.3, pytest-8.3.5, pluggy-1.5.0 -- /home/davydov/PycharmProjects/Python-2025-01-HW01/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/davydov/PycharmProjects/Python-2025-01-HW01
configfile: pyproject.toml
plugins: anyio-4.9.0, cov-6.1.1
collected 3 items

tests/test_app.py::test_check_extension PASSED                                                                                                                                                                                                 [ 33%]
tests/test_app.py::test_parser_string PASSED                                                                                                                                                                                                   [ 66%]
tests/test_app.py::test_calc_table PASSED                                                                                                                                                                                                      [100%]
```


### 2. Оформление:
#### 2.1 Makefile:
```makefile
run:
	python3 ./main.py

test:
	python3 -m pytest -v --color=yes .

lint:
	python3 -m isort .

cov:
	python3 -m pytest --cov
```

#### 2.2 .pre-commit-config.yaml:
```yml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/psf/black
    rev: 25.1.0
    hooks:
      - id: black

-   repo: https://github.com/pycqa/isort
    rev: 6.0.1
    hooks:
      - id: isort
        name: isort (python)

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: 'v1.15.0'  # Use the sha / tag you want to point at
    hooks:
      - id: mypy

-   repo: https://github.com/pycqa/flake8
    rev: 7.2.0  # Pastikan Anda menggunakan versi flake8 terbaru
    hooks:
      - id: flake8

-   repo: https://github.com/christophmeissner/pytest-pre-commit
    rev: 1.0.0
    hooks:
    - id: pytest
      entry: pytest
      language: python
      types: [python]
      require_serial: true
      pass_filenames: false
      always_run: true
      args: [-vv]
```

#### 2.3 CI pipeline:
```yml
name: Python

on: [push, pull_request, workflow_dispatch]

jobs:
  CI-pipeline:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.12]

    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4.1.0
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install poetry
        run: pip install poetry

      - name: Install depends
        run: poetry install --no-interaction

      - name: Lint with flake8
        run: poetry run flake8 --count

      - name: Run black
        run: poetry run black --check .

      - name: Run MyPy
        run: poetry run mypy .

      - name: Run isort
        run: poetry run isort .

      - name: Run Pytest
        run: poetry run pytest -v .
```


#### 2.4 Setup.cfg - конфигурация flake8:
```ini
[flake8]
exclude =
    .git,
    __pycache__,
    venv,
    .venv,
    log,
    reports,
    docs/source/conf.py,
    old,
    build,
    dist
ignore =
    E501,
    E712,
    E722
max-complexity = 10
max-line-length = 88
```

#### 2.5 Параметры для работы пакетов в pyproject.toml:
```toml
[tool.black]
line-length = 88
skip-magic-trailing-comma = false
skip-string-normalization = false
target-version = ['py310','py311','py312']

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
use_parentheses = true
ensure_newline_before_comments = true

[tool.pytest.ini_options]
pythonpath = [
  ".", "src",
]

[tool.mypy]
exclude = [
    'venv',
]
no_namespace_packages = true

[[tool.mypy.overrides]]
module = ["untyped_package.*"]
follow_untyped_imports = true
ignore_missing_imports = true
```
