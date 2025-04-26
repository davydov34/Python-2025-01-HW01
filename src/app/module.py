import configparser
import json
import os
import re
from datetime import datetime
from re import split
from statistics import mean, median

from .logger import logger_app, logger_init


def initConfig(cfg: str):
    """
    Инициализация сервиса из файла конфигурации
    :param cfg:
    :return:
    """
    init_conf: dict = dict()
    try:
        isempty = os.stat(cfg).st_size == 0  # Если файл конфигурации пустой
    except Exception:
        logger_app.exception("File not found!")
    if isempty:
        logger_app.info("Configuation file is empty! Will be use default config!")
        return init_conf

    config = configparser.ConfigParser()
    config.read(cfg)
    cfg_dict = dict(config.items("INIT"))

    if "report_size" in cfg_dict:
        init_conf["report_size"] = int(config["INIT"]["REPORT_SIZE"])
        logger_app.info("Report size cfg get from file...")
    if "report_dir" in cfg_dict:
        init_conf["report_dir"] = config["INIT"]["REPORT_DIR"]
    if "log_dir" in cfg_dict:
        init_conf["log_dir"] = config["INIT"]["LOG_DIR"]
    if "log_file" in cfg_dict:
        init_conf["log_file"] = config["INIT"]["LOG_FILE"]
        logger_init(init_conf["log_file"])
        print(f"Logger start with cfg LOG={init_conf['log_file']}")

    return init_conf


def check_extension(log: str) -> bool:
    """
    Проверяем расширение, в котором находится лог
    :param log:
    :return:
    """
    extension = os.path.splitext(log)[1]
    print(extension)
    for ext in [".gz", ".zip"]:
        if log.endswith(ext):
            logger_app.info("Get log in zip type...")
            return True

    for ext in [".log", ".txt"]:
        if re.match(ext, extension):
            logger_app.info("Get log in plain type...")
            return False

    logger_app.error("File not is a log...")
    exit(1)


tempTupple = ()


def parser_string(line):
    """
    Декомпозиция строки лога
    :param line:
    :return:
    """
    methods = (
        '"GET',
        '"POST',
        '"HEAD',
        '"PUT',
        '"OPTIONS',
    )
    str_list = split(" ", line)  # Разбиение строки
    data = dict()

    if str_list[6] in methods:
        data["url"] = str_list[7]
        try:
            data["time"] = float((str_list[-1]).rstrip())
        except:
            logger_app.error(
                "Position time is not time value!",
                value=(str_list[-1]).rstrip(),
            )
            return "UNPARSED"
        return data
    else:
        return "UNPARSED"


def forming_dataset(file_in, config):
    """
    Функция формирования датасета для вычислений
    :param file_in:
    :param config:
    :return:
    """
    dataset = dict()
    sum_requests = 0
    unparsed_str = 0
    sum_time = 0.0

    with open(file_in, "r", encoding="utf-8") as file:
        while True:
            line = file.readline()
            if not line:
                break
            sum_requests += 1
            line = parser_string(line)
            if line == "UNPARSED":
                unparsed_str += 1
                continue

            sum_time += line["time"]

            if line["url"] in dataset:
                dataset[line["url"]].append(line["time"])
            else:
                dataset[line["url"]] = []
                dataset[line["url"]].append(line["time"])

    return calc_table(
        dataset=dataset,
        config=config,
        sum_requests=sum_requests,
        sum_time=sum_time,
    )


def calc_table(dataset: dict, config, sum_requests, sum_time):
    """
    Функция вычисления значений отчёта
    :param dataset:
    :param config:
    :param sum_requests:
    :param sum_time:
    :return:
    """
    url_sum: dict = dict()  # Общее время ответа на запрос для каждого URL

    for url in dataset:
        url_sum[url] = sum(dataset[url])

    url_sum = {
        k: v
        for k, v in sorted(url_sum.items(), key=lambda item: item[1], reverse=True)[
            : config["REPORT_SIZE"]
        ]
    }

    data_table = list()

    for url in url_sum:
        data_table.append(
            {
                "url": url,
                "count": dataset[url].__len__(),
                "count_perc": dataset[url].__len__() * 100 / sum_requests,
                "time_sum": url_sum[url],
                "time_perc": url_sum[url] / sum_time * 100,
                "time_avg": mean(dataset[url]),
                "time_max": max(dataset[url]),
                "time_med": median(dataset[url]),
            }
        )
    del dataset
    del url_sum

    return json.dumps(data_table)


def create_html(table_json, path_reports, date_log: datetime):
    """
    Функция генерации отчёта в html-формате
    :param table_json:
    :return:
    """
    try:
        file_report = open("src/templates/report.html", "r", encoding="utf-8")
    except FileNotFoundError:
        logger_app.error("Template for report not Found!")
        logger_app.exception()
    else:
        with file_report as file:
            html_text = file.read().replace("$table_json", table_json)
            output_file = os.path.join(
                path_reports, f"report-{date_log.strftime('%Y.%m.%d')}.html"
            )

            try:
                with open(output_file, "w", encoding="utf-8") as res:
                    res.write(html_text)
                    logger_app.info("Report success created!", report_name=output_file)
            except:
                logger_app.error(
                    "Error with writing report file!", report_name=output_file
                )
                logger_app.exception()

    # shutil.copyfile(os.path.join('src/templates/','jquery.tablesorter.min.js'), os.path.join(path_reports, 'jquery.tablesorter.min.js'))
    # shutil.copyfileobj('templates/jquery.tablesorter.min.js', os.path.join(path_reports, 'jquery.tablesorter.min.js'))
