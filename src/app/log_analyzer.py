# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import datetime
import gzip
import os
import re
import shutil
import sys
from os.path import isfile, join

from .logger import logger_app
from .module import check_extension, create_html, forming_dataset, initConfig

config = {"REPORT_SIZE": 1000, "REPORT_DIR": "reports", "LOG_DIR": "log"}


def read_log(file, is_archive: bool, config) -> dict:
    if is_archive:
        try:
            with gzip.open(file, "rb") as file_in:
                with open("parsing.log", "wb") as file_out:
                    shutil.copyfileobj(file_in, file_out)
        except:
            logger_app.exception("Ошибка открытия лог-файла!")

        output_json = forming_dataset(file_in="parsing.log", config=config)
        os.remove("parsing.log")
        return output_json
    else:
        return forming_dataset(file_in=file, config=config)


def run_analyze(cfg):
    outer_cfg = initConfig(cfg)
    for param in outer_cfg:
        config[param.upper()] = outer_cfg[param.lower()]

    log_dir = config["LOG_DIR"]

    logs = [
        f
        for f in os.listdir(log_dir)
        if isfile(join(log_dir, f)) and f.__contains__("nginx-access-ui.log-")
    ]
    if not logs:
        logger_app.info("The log files do not exist!")
        sys.exit(0)

    try:
        str_date_dict = {
            d: datetime.datetime.strptime("".join(filter(str.isdigit, d)), "%Y%m%d")
            for d in logs
        }
        last_log = os.path.join(
            config["LOG_DIR"], max(str_date_dict, key=str_date_dict.get)
        )
        logger_app.info(f"Last log is {last_log}")
    except Exception:
        logger_app.error("Filename have invalid format of date!")
        sys.exit(1)

    date_log = max(str_date_dict.values())
    list_reports = os.listdir(config["REPORT_DIR"])
    if not list_reports:
        list_reports.append("19700101")

    last_report = max(
        [
            (datetime.datetime.strptime("".join(re.findall(r"\d+", f)), "%Y%m%d"))
            for f in list_reports
        ]
    )

    if date_log == last_report:
        logger_app.info("Not data for execute...")
    else:
        table_json = read_log(
            file=last_log, is_archive=check_extension(last_log), config=config
        )
        create_html(table_json, config["REPORT_DIR"], date_log)
