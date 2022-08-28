# == combine_two_pvoutput_systems.py Author: Zuinige Rijder ==================
"""
Simple Python3 script to combine two PVOutput Systems continously
(normally once per 5 minutes) into target PVOutput System.
"""
import time
import sys
import configparser
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request

# == read api_secrets in combine_two_pvoutput_systems.cfg ====================
parser = configparser.ConfigParser()
parser.read('combine_two_pvoutput_systems.cfg')
api_secrets = dict(parser.items('api_secrets'))

# == Secrets, fill in yours in combine_two_pvoutput_systems.cfg ==============
PVOUTPUT_SOURCE1_API_KEY = api_secrets['pvoutput_source1_api_key']
PVOUTPUT_SOURCE1_SYSTEM_ID = api_secrets['pvoutput_source1_system_id']

PVOUTPUT_SOURCE2_API_KEY = api_secrets['pvoutput_source2_api_key']
PVOUTPUT_SOURCE2_SYSTEM_ID = api_secrets['pvoutput_source2_system_id']

PVOUTPUT_TARGET_API_KEY = api_secrets['pvoutput_target_api_key']
PVOUTPUT_TARGET_SYSTEM_ID = api_secrets['pvoutput_target_system_id']

# == Constants ===============================================================
PVOUTPUT_GET_URL = 'https://pvoutput.org/service/r2/getstatus.jsp'
PVOUTPUT_ADD_URL = 'http://pvoutput.org/service/r2/addbatchstatus.jsp'

GET_SOURCE_1_URL = PVOUTPUT_GET_URL + \
    '?key=' + PVOUTPUT_SOURCE1_API_KEY + \
    '&sid=' + PVOUTPUT_SOURCE1_SYSTEM_ID + \
    '&h=1&asc=0&limit=288'
GET_SOURCE_2_URL = PVOUTPUT_GET_URL + \
    '?key=' + PVOUTPUT_SOURCE2_API_KEY + \
    '&sid=' + PVOUTPUT_SOURCE2_SYSTEM_ID + \
    '&h=1&asc=0&limit=288'
GET_TARGET_URL = PVOUTPUT_GET_URL + \
    '?key=' + PVOUTPUT_TARGET_API_KEY + \
    '&sid=' + PVOUTPUT_TARGET_SYSTEM_ID + \
    '&h=1&asc=0&limit=288'
TARGET_HEADERS = {
    'X-Pvoutput-Apikey': PVOUTPUT_TARGET_API_KEY,
    'X-Pvoutput-SystemId': PVOUTPUT_TARGET_SYSTEM_ID,
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/plain'
}

TODAY = datetime.now().strftime("%Y%m%d")  # format yyyymmdd


# == log =====================================================================
def log(msg):
    """log a message prefixed with a date/time format yyyymmdd hh:mm:ss"""
    print(TODAY + datetime.now().strftime(" %H:%M:%S") + ': ' + msg)


# == print_splitted ==========================================================
def print_splitted(content):
    """print parameter splitted by ; line by line"""
    count = 0
    for item in content.split(';'):
        count += 1
        print(str(count) + ': ' + item)


# == execute_request =========================================================
def execute_request(url, request) -> str:
    """execute request and log url in case of errors"""
    errorstring = ''
    try:
        with urlopen(request, timeout=10) as response:
            body = response.read()
            content = body.decode("utf-8")
            return content
    except HTTPError as error:
        errorstring = str(error.status) + ': ' + error.reason
    except URLError as error:
        errorstring = str(error.reason)
    except TimeoutError:
        errorstring = 'Request timed out'

    log('ERROR: ' + url + ' -> ' + errorstring)
    time.sleep(60)  # retry after 1 minute

    return 'ERROR'


# == add_datapoints ==========================================================
def add_datapoints(datapoints_count, datapoints_str) -> str:
    """add datapoints"""
    log('Target datapoints: ' + str(datapoints_count))
    print_splitted(datapoints_str)
    post_data = datapoints_str.encode("utf-8")
    retry = 0
    while True:
        retry += 1
        request = Request(
            PVOUTPUT_ADD_URL, data=post_data, headers=TARGET_HEADERS)
        content = execute_request(PVOUTPUT_ADD_URL, request)
        if content != 'ERROR' or retry > 30:
            if content == 'ERROR':
                log('ERROR: number of retries exceeded')
            return content


# == get_pvoutput_entries_today ==============================================
def get_pvoutput_entries_today(url) -> str:
    """get pvoutput entries since time today"""
    request_url = url + '&d="' + TODAY + '"'
    while True:
        request = Request(request_url)
        content = execute_request(request_url, request)
        if content != 'ERROR':
            return content


# == compute_minutes =========================================================
def compute_minutes(content) -> int:
    """compute minutes for this day with the first time"""
    minutes = 300  # start at 5 hours
    if len(content) > 14 and content[0:8] == TODAY:
        minutes = round(int(content[9:11]) * 60 + int(content[12:14]))
    return minutes


# == minutes_to_hhmm =========================================================
def minutes_to_hhmm(minutes) -> str:
    """Convert minutes to timestring in format hh:mm"""
    hours = int(minutes / 60)
    rounded_minutes = round(minutes - (60 * hours))
    hhmm = f"{hours:02d}" + ':' + f"{rounded_minutes:02d}"
    return hhmm


# prev tuple index CONSTANTS
LINE_TUPLE_INDEX = 0
WH_TUPLE_INDEX = 1
VOLT_STR_TUPLE_INDEX = 2


# == process_one_pvoutput_result =============================================
def process_one_pvoutput_result(
    line,
    prev,  # tuple (prev_line, prev_wh, prev_volt_str)
    target_minutes,
    minutes_dict
) -> tuple[int, int, str, str]:
    """process one pvoutput result"""
    (date_str, time_str, watthour_str, _, watt_str,
        _, _, _, _, _, volt_str) = line.split(',')
    if date_str != TODAY:  # skip dates not today
        return 0, 0, '0', ''  # not interested in other days

    watthour = int(watthour_str)
    if volt_str == 'NaN':
        volt_str = prev[VOLT_STR_TUPLE_INDEX]  # just use previous volt value

    minutes = compute_minutes(line)
    if minutes % 5 != 0:
        sys.exit('Minutes not in 5 minutes increments: ' + line)

    line = date_str + ',' + \
        time_str + ',' + str(watthour) + ',' + watt_str + ',,,,' + volt_str
    if minutes > target_minutes:
        if prev[LINE_TUPLE_INDEX] == '':
            prev_minutes = minutes - 5  # no missing entries
        else:
            prev_minutes = compute_minutes(prev[LINE_TUPLE_INDEX])
            minutes_dict[prev_minutes] = prev[LINE_TUPLE_INDEX]

        if prev_minutes + 5 != minutes:
            print(
                'Missing entry:\n---> ' +
                prev[LINE_TUPLE_INDEX] + '\n---> ' + line)
            missing_entries = int(((minutes - prev_minutes - 5) / 5))
            watthour = int(
                prev[WH_TUPLE_INDEX] +
                ((watthour - prev[WH_TUPLE_INDEX]) / (1 + missing_entries))
            )
            time_str = minutes_to_hhmm(prev_minutes + 5)
            added_line = date_str + ',' + \
                time_str + ',' + str(watthour) + \
                ',' + watt_str + ',,,,' + volt_str

            print('Prev : ' + prev[LINE_TUPLE_INDEX])
            print('Added: ' + added_line)
            print('Next : ' + line + '\n')
            minutes_dict[prev_minutes + 5] = added_line
            line = added_line
        else:
            minutes_dict[minutes] = line

    return minutes, watthour, volt_str, line


# == read_entries_in_memory_with_5_minutes_intervals =========================
def read_entries_in_memory_with_5_minutes_intervals(
    prefix,
    content,
    written_target_minutes,
    written_watthour
) -> tuple[int, dict]:
    """read entries in memory with 5 minutes intervals"""
    since_time = minutes_to_hhmm(written_target_minutes)
    minutes_dict = {}
    splitted = content.split(';')
    prev_line = ''
    prev_wh = written_watthour
    prev_volt_str = '0'
    written_hhmm = since_time
    i = len(splitted) - 1
    while i >= 0:
        line = splitted[i]
        i -= 1

        prev_minutes = compute_minutes(prev_line)
        minutes, prev_wh, prev_volt_str, line = process_one_pvoutput_result(
            line, (prev_line, prev_wh, prev_volt_str), written_target_minutes,
            minutes_dict)
        if line == '':
            continue  # skip empty lines

        if minutes <= written_target_minutes:
            written_hhmm = minutes_to_hhmm(minutes)
            written_watthour = prev_wh
        else:
            if prev_line != '' and prev_minutes + 5 != minutes:
                i += 1  # do this entry again next loop

        prev_line = line

    log(prefix +
        ' read_in_memory since ' + since_time + ': written=' + written_hhmm +
        ', written wh=' + str(written_watthour) + ', wh=' + str(prev_wh) +
        ', line=' + prev_line)
    return written_watthour, minutes_dict


# == compute_values ==========================================================
def compute_values(
    source_dict, from_minutes, written_watthour
) -> tuple[int, int, float, int]:
    """compute watthour, watt, volt and last written watthour"""
    watthour = 0
    watt = 0
    volt = 0.0
    if from_minutes in source_dict:
        line = source_dict[from_minutes]
        _, _, watthour_str, watt_str, _, _, _, volt_str = line.split(',')
        written_watthour = int(watthour_str)
        watt = int(watt_str)
        volt = float(volt_str)

    watthour = written_watthour

    return watthour, watt, volt, written_watthour


# == compute_combined_values =================================================
def compute_combined_values(
    source_1_dict,
    source_2_dict,
    from_minutes,
    written_watthour_1,
    written_watthour_2
) -> tuple[int, int, float, int, int]:
    """compute combined values of source 1 and 2"""
    watthour, watt, volt, written_watthour_1 = compute_values(
        source_1_dict, from_minutes, written_watthour_1)

    watthour2, watt2, volt2, written_watthour_2 = compute_values(
        source_2_dict, from_minutes, written_watthour_2)

    watthour += watthour2
    watt += watt2
    volt += volt2

    return (
        watthour,
        watt,
        volt,
        written_watthour_1,
        written_watthour_2
    )


# == compute_from_and_to_minutes =============================================
def compute_from_and_to_minutes(
    source_1_dict, source_2_dict
) -> tuple[int, int]:
    """compute from_minutes and to_minutes"""

    # Since python 3.7 the order is insertion
    # so the minimum of first entries and last entries can be computed
    source_1_keys = list(source_1_dict.keys())
    source_2_keys = list(source_2_dict.keys())
    len1 = len(source_1_keys)
    len2 = len(source_2_keys)
    if len1 > 0 and len2 > 0:
        from_minutes = min(source_1_keys[0], source_2_keys[0])
        to_minutes = min(source_1_keys[len1-1], source_2_keys[len2-1])
    elif len1 > 0:
        from_minutes = source_1_keys[0]
        to_minutes = source_1_keys[len1-1]
    else:
        from_minutes = source_2_keys[0]
        to_minutes = source_2_keys[len2-1]

    return from_minutes, to_minutes


# == construct_and_add_datapoints ===========================================
def construct_and_add_datapoints(
    pvoutput_string, datapoints_count, datapoints_str
) -> tuple[int, str]:
    """construct and add datapoints if above 29"""
    datapoints_count += 1
    if datapoints_count > 1:
        datapoints_str += ';'
    datapoints_str += pvoutput_string
    if datapoints_count >= 29:
        add_datapoints(datapoints_count, datapoints_str)
        datapoints_str = 'data='
        datapoints_count = 0

    return datapoints_count, datapoints_str


# == process_sources_entries =================================================
def process_sources_entries(
    source_1_dict,
    source_2_dict,
    written_target_minutes,
    written_watthour_1,
    written_watthour_2
) -> tuple[int, int]:
    """process sources entries"""
    datapoints_count = 0
    datapoints_str = 'data='

    from_minutes, to_minutes = compute_from_and_to_minutes(
        source_1_dict, source_2_dict)
    while from_minutes <= to_minutes:
        watthour, watt, volt, written_watthour_1, written_watthour_2 = \
            compute_combined_values(
                source_1_dict,
                source_2_dict,
                from_minutes,
                written_watthour_1,
                written_watthour_2
            )

        # only write when AFTER last target time
        if from_minutes > written_target_minutes:
            pvoutput_string = (
                TODAY + ',' +
                minutes_to_hhmm(from_minutes) + ',' +
                str(watthour) + ',' + str(watt) + ',,,,' + str(round(volt))
            )
            datapoints_count, datapoints_str = construct_and_add_datapoints(
                pvoutput_string, datapoints_count, datapoints_str)

        from_minutes += 5  # next 5 minutes

    if datapoints_count > 0:
        add_datapoints(datapoints_count, datapoints_str)

    return written_watthour_1, written_watthour_2


# == compute_entries_since ===================================================
def compute_entries_since(
    prefix, url, written_target_minutes, written_watthour
) -> tuple[int, int, dict]:
    """compute dictionary entries since time"""
    content = get_pvoutput_entries_today(url)
    current_minutes = compute_minutes(content)
    minutes_dict = {}
    written_watthour = 0
    if current_minutes > written_target_minutes:
        written_watthour, minutes_dict = \
            read_entries_in_memory_with_5_minutes_intervals(
                prefix, content,
                written_target_minutes, written_watthour
            )

    return current_minutes, written_watthour, minutes_dict


# == main_loop ===============================================================
def main_loop():
    """main loop"""
    # get the latest values
    written_target_minutes, _, _ = compute_entries_since(
        'Target  ', GET_TARGET_URL, 300, 0)
    log("Last Written target: " + minutes_to_hhmm(written_target_minutes))
    written_minutes_1, written_watthour_1, _ = compute_entries_since(
        'Source 1', GET_SOURCE_1_URL, written_target_minutes, 0)
    written_minutes_2, written_watthour_2, _ = compute_entries_since(
        'Source 2', GET_SOURCE_2_URL, written_target_minutes, 0)
    log('Sleeping till next 5 minutes plus 3 minutes')

    while True:
        now = datetime.now()
        time.sleep(480 - (int(now.timestamp()) % 300))  # next 5+3 minutes incr

        # only check between 5 and 23 hours
        if now.hour < 5 or now.hour > 22:
            log('Outside solar generation hours (5..23)')
            sys.exit('Exiting program to start fresh tomorrow')

        written_minutes_1, _, source_1_dict = compute_entries_since(
            'Source 1', GET_SOURCE_1_URL, written_target_minutes,
            written_watthour_1)
        if written_minutes_1 <= written_target_minutes and now.hour != 22:
            # when after 22:00 if there are results, process them anyway
            # because other inverter might be sleeping
            continue  # nothing to do

        written_minutes_2, _, source_2_dict = compute_entries_since(
            'Source 2', GET_SOURCE_2_URL, written_target_minutes,
            written_watthour_2)
        if written_minutes_2 <= written_target_minutes and now.hour != 22:
            # when after 22:00 if there are results, process them anyway
            # because other inverter might be sleeping
            continue  # nothing to do

        if (written_minutes_1 <= written_target_minutes and
                written_minutes_2 <= written_target_minutes):
            continue  # nothing to do

        written_watthour_1, written_watthour_2 = \
            process_sources_entries(
                source_1_dict,
                source_2_dict,
                written_target_minutes,
                written_watthour_1,
                written_watthour_2
            )

        written_target_minutes = min(written_minutes_1, written_minutes_2)


# == MAIN ====================================================================
main_loop()
