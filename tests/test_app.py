import json
import os
import sys

from src.app.module import calc_table, check_extension, parser_string

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


def test_check_extension():
    assert check_extension("log.gz") == True
    assert check_extension("log.zip") == True
    assert check_extension("log.log") == False
    assert check_extension("log.txt") == False


def test_parser_string():
    set = '1.169.137.128 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/16803530 HTTP/1.1" 200 6766 "-" "Slotovod" "-" "1498697423-2118016444-4708-9752781" "712e90144abee9" 0.156'
    fail_set = '1.202.56.176 -  - [29/Jun/2017:04:15:18 +0300] "0" 400 166 "-" "-" "-" "-" "-" 0.001'
    fail_set2 = '1.202.56.176 -  - [29/Jun/2017:04:15:18 +0300] "0" 400 166 "-" "-" "-" "-" "-" 0.0x1'
    assert isinstance(parser_string(set), dict) == True
    assert parser_string(set)["url"] == "/api/v2/banner/16803530"
    assert isinstance(parser_string(set)["time"], float) == True
    assert parser_string(set)["time"] == 0.156
    assert parser_string(fail_set) == "UNPARSED"
    assert parser_string(fail_set2) == "UNPARSED"


def test_calc_table():
    config = dict()
    config["REPORT_SIZE"] = 1
    dataset = {
        "/1/": [0.1, 0, 2, 0, 3, 0.4],
        "/2/": [1.0, 2.0, 3.0, 4.0],
    }

    json_data = calc_table(dataset, config, 8, 11)
    dict_from_json = json.loads(json_data)
    print(f"Test result: {dict_from_json}")
    assert dict_from_json[0]["url"] == "/2/"
    assert dict_from_json[0]["count"] == 4
    assert dict_from_json[0]["count_perc"] == 50
    assert dict_from_json[0]["time_sum"] == 10
    assert dict_from_json[0]["time_perc"] > 90
    assert dict_from_json[0]["count"] == 4
    assert dict_from_json[0]["time_max"] == 4.0
    assert dict_from_json[0]["time_med"] == 2.5
    assert dict_from_json[0]["time_med"] == 2.5
