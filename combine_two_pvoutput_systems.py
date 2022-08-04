# == combine_two_pvoutput_systems.py Author: Zuinige Rijder ==================
"""
Simple Python3 script to combine two PVOutput Systems continously
(normally once per 5 minutes) into target PVOutput System.
"""
import time
import sys
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request

# == Secrets, fill in yours ==================================================
PVOUTPUT_SOURCE1_API_KEY = 'xxxx'
PVOUTPUT_SOURCE1_SYSTEM_ID = 'xxxx'

PVOUTPUT_SOURCE2_API_KEY = 'xxxx'
PVOUTPUT_SOURCE2_SYSTEM_ID = 'xxxx'

PVOUTPUT_TARGET_API_KEY = 'xxxx'
PVOUTPUT_TARGET_SYSTEM_ID = 'xxxx'

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


# == now_yyyymmdd ============================================================
def now_yyyymmdd():
    """return now yymmdd string"""
    return datetime.now().strftime("%Y%m%d")


# == log =====================================================================
def log(msg):
    """log a message prefixed with a date/time format yyyymmdd hh:mm:ss"""
    print(datetime.now().strftime("%Y%m%d %H:%M:%S") + ': ' + msg)


# == print_splitted ==========================================================
def print_splitted(content):
    """print parameter splitted by ; line by line"""
    count = 0
    for item in content.split(';'):
        count = count + 1
        print(str(count) + ': ' + item)


# ==  get_or_post=============================================================
def get_or_post(prefix, url, request) -> str:
    """get or post url request with prefix logged"""
    log(prefix)
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


# == get =====================================================================
def get(prefix, url) -> str:
    """get url request with prefix logged"""
    request = Request(url)
    content = get_or_post('GET ' + prefix, url, request)
    return content


# == post ====================================================================
def post(url, data, headers) -> str:
    """post url data with headers"""
    post_data = data.encode("utf-8")
    request = Request(url, data=post_data, headers=headers)
    content = get_or_post('POST Target', url, request)
    return content


# == add_datapoints ==========================================================
def add_datapoints(datapoints_count, datapoints_str) -> str:
    """add datapoints"""
    log('Target datapoints: ' + str(datapoints_count))
    print_splitted(datapoints_str)
    retry = 0
    while True:
        retry = retry + 1
        content = post(PVOUTPUT_ADD_URL, datapoints_str, TARGET_HEADERS)
        if content != 'ERROR' or retry > 10:
            return content


# == get_status ==============================================================
def get_status(prefix, url, since_hhmm) -> str:
    """get status with prefix and parameters logged"""
    parameters = '&d="' + now_yyyymmdd() + '"&t="' + since_hhmm + '"'
    request_url = url + parameters
    content = get(prefix + ' ' + parameters, request_url)
    return content


# == compute_minutes =========================================================
def compute_minutes(content) -> int:
    """compute minutes for this day with the first time"""
    minutes = 300  # start at 5 hours
    if len(content) > 14 and content[0:8] == now_yyyymmdd():
        minutes = round(int(content[9:11]) * 60 + int(content[12:14]))
    return minutes


# == minutes_to_hhmm =========================================================
def minutes_to_hhmm(minutes) -> str:
    """Convert minutes to timestring in format hh:mm"""
    hours = int(minutes / 60)
    rounded_minutes = round(minutes - (60 * hours))
    hhmm = f"{hours:02d}" + ':' + f"{rounded_minutes:02d}"
    return hhmm


# == process_line ==========================================================
def process_line(line, prev_line, prev_wh, target_minutes, minutes_dict):
    """process line"""
    (date_str, time_str, watthour_str, _, watt_str,
        _, _, _, _, _, volt_str) = line.split(',')
    if date_str != now_yyyymmdd():  # skip dates not today
        return 0, 0, ''  # not interested in other days

    watthour = int(watthour_str)
    if volt_str == 'NaN':
        volt_str = '0'

    minutes = compute_minutes(line)
    if minutes % 5 != 0:
        sys.exit('Minutes not in 5 minutes increments: ' + line)

    line = date_str + ',' + \
        time_str + ',' + str(watthour) + ',' + watt_str + ',,,,' + volt_str
    if minutes > target_minutes:
        if prev_line == '':
            prev_minutes = minutes - 5  # no missing entries
        else:
            prev_minutes = compute_minutes(prev_line)
            minutes_dict[prev_minutes] = prev_line

        if prev_minutes + 5 != minutes:
            print('Missing entry:\n---> ' + prev_line + '\n---> ' + line)
            missing_entries = int(((minutes - prev_minutes - 5) / 5))
            # print('Number of missing entries: ' + str(missingEntries))
            watthour = int(
                prev_wh + ((watthour - prev_wh) / (1 + missing_entries))
            )
            time_str = minutes_to_hhmm(prev_minutes + 5)
            added_line = date_str + ',' + \
                time_str + ',' + str(watthour) + \
                ',' + watt_str + ',,,,' + volt_str

            print('Prev : ' + prev_line)
            print('Added: ' + added_line)
            print('Next : ' + line + '\n')
            minutes_dict[prev_minutes + 5] = added_line
            line = added_line
        else:
            minutes_dict[minutes] = line

    return minutes, watthour, line


# == read_in_memory ==========================================================
def read_in_memory(
    prefix,
    content,
    written_target_minutes,
    written_watthour
):
    """read content in memory with 5 minutes intervals"""
    since_time = minutes_to_hhmm(written_target_minutes)
    log(prefix + ' read_in_memory since: ' + since_time)
    minutes_dict = {}
    splitted = content.split(';')
    prev_line = ''
    prev_wh = written_watthour
    written_hhmm = since_time
    i = len(splitted) - 1
    while i >= 0:
        line = splitted[i]
        i -= 1

        prev_minutes = compute_minutes(prev_line)
        minutes, watthour, line = process_line(
            line, prev_line, prev_wh, written_target_minutes,
            minutes_dict)
        if line == '':
            continue  # skip empty lines

        if minutes <= written_target_minutes:
            written_hhmm = minutes_to_hhmm(minutes)
            written_watthour = watthour
        else:
            if prev_line != '' and prev_minutes + 5 != minutes:
                i += 1  # do this entry again next loop

        prev_line = line
        prev_wh = watthour

    log(prefix +
        ' read_in_memory last values: written time=' + written_hhmm +
        ', written wh=' + str(written_watthour) + ', wh=' + str(prev_wh) +
        ', line=' + prev_line)
    return written_watthour, minutes_dict


# == compute_values ==========================================================
def compute_values(source_dict, from_minutes, written_watthour):
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
):
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
def compute_from_and_to_minutes(source_1_dict, source_2_dict):
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
):
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


# == process ===============================================================
def process(
    source_1_dict,
    source_2_dict,
    written_target_minutes,
    written_watthour_1,
    written_watthour_2
):
    """process"""
    log("Processing....")
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
                now_yyyymmdd() + ',' +
                minutes_to_hhmm(from_minutes) + ',' +
                str(watthour) + ',' + str(watt) + ',,,,' + str(round(volt))
            )
            datapoints_count, datapoints_str = construct_and_add_datapoints(
                pvoutput_string, datapoints_count, datapoints_str)

        from_minutes += 5  # next 5 minutes

    if datapoints_count > 0:
        add_datapoints(datapoints_count, datapoints_str)

    return written_watthour_1, written_watthour_2


# == compute_dictionary ======================================================
def compute_dictionary(
    prefix, url, written_target_minutes, written_watthour
):
    """compute dictionary"""
    since_hhmm = minutes_to_hhmm(written_target_minutes)
    content = get_status(prefix, url, since_hhmm)
    current_minutes = compute_minutes(content)
    minutes_dict = {}
    written_watthour = 0
    if current_minutes > written_target_minutes:
        written_watthour, minutes_dict = \
            read_in_memory(
                prefix, content,
                written_target_minutes, written_watthour
            )

    return current_minutes, written_watthour, minutes_dict


# == main_loop ===============================================================
def main_loop():
    """main loop"""
    # get the latest values
    written_target_minutes, _, _ = compute_dictionary(
        'Target  ', GET_TARGET_URL, 300, 0)
    log("Last Written target: " + minutes_to_hhmm(written_target_minutes))
    written_minutes_1, written_watthour_1, _ = compute_dictionary(
        'Source 1', GET_SOURCE_1_URL, written_target_minutes, 0)
    written_minutes_2, written_watthour_2, _ = compute_dictionary(
        'Source 2', GET_SOURCE_2_URL, written_target_minutes, 0)

    while True:
        log('Sleeping for 5 minutes')
        time.sleep(300)  # wait 5 minutes before checking again

        # only check between 5 and 23 hours
        hour_now = datetime.now().hour
        if hour_now < 5 or hour_now > 22:
            log('Outside solar generation hours (5..23)')
            sys.exit('Exiting program to start fresh tomorrow')

        written_minutes_1, _, source_1_dict = compute_dictionary(
            'Source 1', GET_SOURCE_1_URL, written_target_minutes,
            written_watthour_1)
        if written_minutes_1 <= written_target_minutes and hour_now != 22:
            # when after 22:00 if there are results, process them anyway
            # because other inverter might be sleeping
            continue  # nothing to do

        written_minutes_2, _, source_2_dict = compute_dictionary(
            'Source 2', GET_SOURCE_2_URL, written_target_minutes,
            written_watthour_2)
        if written_minutes_2 <= written_target_minutes and hour_now != 22:
            # when after 22:00 if there are results, process them anyway
            # because other inverter might be sleeping
            continue  # nothing to do

        if (written_minutes_1 <= written_target_minutes and
                written_minutes_2 <= written_target_minutes):
            continue  # nothing to do

        written_watthour_1, written_watthour_2 = \
            process(
                source_1_dict,
                source_2_dict,
                written_target_minutes,
                written_watthour_1,
                written_watthour_2
            )

        written_target_minutes = min(written_minutes_1, written_minutes_2)


# == MAIN ====================================================================
main_loop()
