#== CombinePVOutputSystems.py Author: Zuinige Rijder ====================
import time
import sys
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request

#== Secrets, fill in yours ====================================================
PVOUTPUT_SOURCE1_API_KEY = 'xxxx'
PVOUTPUT_SOURCE1_SYSTEM_ID = 'xxxx'

PVOUTPUT_SOURCE2_API_KEY = 'xxxx'
PVOUTPUT_SOURCE2_SYSTEM_ID = 'xxxx'

PVOUTPUT_TARGET_API_KEY = 'xxxx'
PVOUTPUT_TARGET_SYSTEM_ID = 'xxxx'

#== Constants =================================================================
PVOUTPUT_GET_STATUS_URL = 'https://pvoutput.org/service/r2/getstatus.jsp'
PVOUTPUT_ADD_BATCH_STATUS_URL = 'http://pvoutput.org/service/r2/addbatchstatus.jsp'

GET_PVOUTPUT_SOURCE1_GET_STATUS_URL = PVOUTPUT_GET_STATUS_URL + '?key=' +  PVOUTPUT_SOURCE1_API_KEY + '&sid=' + PVOUTPUT_SOURCE1_SYSTEM_ID + '&h=1&asc=0&limit=288'; 
GET_PVOUTPUT_SOURCE2_GET_STATUS_URL = PVOUTPUT_GET_STATUS_URL + '?key=' +  PVOUTPUT_SOURCE2_API_KEY + '&sid=' + PVOUTPUT_SOURCE2_SYSTEM_ID + '&h=1&asc=0&limit=288'; 
GET_PVOUTPUT_TARGET_GET_STATUS_URL = PVOUTPUT_GET_STATUS_URL + '?key=' +  PVOUTPUT_TARGET_API_KEY + '&sid=' + PVOUTPUT_TARGET_SYSTEM_ID + '&h=1&asc=0&limit=288'; 
PVOUTPUT_TARGET_HEADER = {'X-Pvoutput-Apikey': PVOUTPUT_TARGET_API_KEY, 'X-Pvoutput-SystemId': PVOUTPUT_TARGET_SYSTEM_ID, 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}

#== log ======================================================================= 
def log(msg):
    print(datetime.now().strftime("%Y%m%d %H:%M:%S") + ': ' + msg)

#== printSplitted ======================================================================= 
def printSplitted(content):
    count = 0
    for item in content.split(';'):
        count = count + 1
        print(str(count) + ': ' + item)

#==  getOrPost======================================================================
def getOrPost(prefix, url, request) -> str: 
    log(prefix)
    errorstring = ''
    try:
        with urlopen(request, timeout=10) as response:
            body = response.read()
            content = body.decode("utf-8")
            #log('Content=')
            #printSplitted(content)
            return content
    except HTTPError as error:
        errorstring = str(error.status) + ': ' + error.reason
    except URLError as error:
        errorstring = str(error.reason)
    except TimeoutError:
         errorstring = 'Request timed out'

    log('ERROR: ' + url + ' -> ' + errorstring)
    time.sleep(60) # retry after 1 minute

    return 'ERROR'

#== get ======================================================================
def get(prefix, url) -> str: 
    request = Request(url)
    content = getOrPost('GET ' + prefix, url, request)
    return content

#== post ======================================================================
def post(url, data, header) -> str: 
    post_data = data.encode("utf-8")
    request = Request(url, data=post_data, headers=header)
    content = getOrPost('POST Target', url, request)
    return content
    
#== addbatchstatus ==============================================================
def addBatchStatus(dataPointsCount, dataPointsStr) -> str:
    log('Target datapoints: ' + str(dataPointsCount))
    printSplitted(dataPointsStr)
    #return 'OK'
    retry = 0
    while True:
        retry = retry + 1
        content = post(PVOUTPUT_ADD_BATCH_STATUS_URL, dataPointsStr, PVOUTPUT_TARGET_HEADER)
        if content != 'ERROR' or retry > 10:
            return content 

#== getStatus ==============================================================
def getStatus(prefix, url, dateString, timeString) -> str:
    parameters = '&d="' + dateString + '"&t="' + timeString + '"'
    requestUrl = url + parameters
    content = get(prefix + ' ' + parameters, requestUrl)
    return content

#== computeMinutes ==============================================================
def computeMinutes(dateString, content) -> int:
    minutes = 300 # start at 5 hours
    if len(content) > 14 and content[0:8] == dateString:
        minutes = round(int(content[9:11]) * 60 + int(content[12:14]))
    #print('computeMinutes(' + content[9:14] + ') = ' + str(minutes))
    return minutes

#== minutesToTimeString ==============================================================
def minutesToTimeString(minutes) -> str:
    hours = int(minutes / 60)
    min = round(minutes - (60 * hours))
    timeStr = "%02d" % hours + ':' + "%02d" % min
    #print('minutesToTimeString(' + str(minutes) + ') = ' + timeStr)
    return timeStr

#== readInMemory ==============================================================
def readInMemory(prefix, content, dateString, targetMinutes, lastWrittenWh):
    sinceTime = minutesToTimeString(targetMinutes)
    log(prefix + ' readInMemory since: ' + sinceTime)
    minutes2result = {}
    splitted = content.split(';')
    prevLine = ''
    prevWh = lastWrittenWh
    lastWrittenTime = sinceTime
    i = len(splitted) - 1
    while i >= 0:
        line = splitted[i]
        #print('Lineno ', i, ': ', line)
        i -= 1
        
        d, t, whStr, energyEfficiency, w, averagePower, normalisedOutput, energyConsumption, PowerConsumption, temp, v = line.split(',')
        if d != dateString: # skip dates not today
            continue # not interested in other days

        wh = int(whStr)
        if v == 'NaN':
            v = '0'

        minutes = computeMinutes(dateString, line)
        if minutes % 5 != 0:
            sys.exit('Minutes not in 5 minutes increments: ' + line)
        
        line = d + ',' + t + ',' + str(wh) + ',' + w + ',,,,' + v
        if minutes > targetMinutes:
            if prevLine == '':
                prevMinutes = minutes - 5 # no missing entries
            else:
                prevMinutes = computeMinutes(dateString, prevLine)
                minutes2result[prevMinutes] = prevLine
                
            if prevMinutes + 5 != minutes:
                print('Missing entry:\n---> ' + prevLine + '\n---> ' + line)
                missingEntries = int(((minutes - prevMinutes - 5) / 5))
                #print('Number of missing entries: ' + str(missingEntries))
                wh = int(prevWh + ((wh - prevWh) / (1 + missingEntries)))
                t = minutesToTimeString(prevMinutes + 5)
                addedLine = d + ',' + t + ',' + str(wh) + ',' + w + ',,,,' + v
                
                print('Prev : ' + prevLine)
                print('Added: ' + addedLine)
                print('Next : ' + line + '\n')
                minutes2result[prevMinutes + 5] = addedLine
                line = addedLine
                i += 1 # do this entry again next loop
            else:
                minutes2result[minutes] = line
                #print('Entry: ' + line)
        else:
            lastWrittenTime = minutesToTimeString(minutes)
            lastWrittenWh = wh
            
        prevLine = line
        prevWh = wh

    log(prefix + ' readInMemory last values: written time=' + lastWrittenTime + ', written wh=' + str(lastWrittenWh) + ', wh=' + str(prevWh) + ', line=' + prevLine)
    return minutes2result, lastWrittenWh

#== MAIN ======================================================================

# get the latest combined target time
now = datetime.now()
dateString = now.strftime("%Y%m%d")
target = getStatus('Target  ', GET_PVOUTPUT_TARGET_GET_STATUS_URL, dateString, '05:00')
lastTargetMinutes = computeMinutes(dateString, target)
source1Content = getStatus('Source 1', GET_PVOUTPUT_SOURCE1_GET_STATUS_URL, dateString, '05:00')
lastSource1Minutes = computeMinutes(dateString, source1Content)
source2Content = getStatus('Source 2', GET_PVOUTPUT_SOURCE2_GET_STATUS_URL, dateString, '05:00')
lastSource2Minutes = computeMinutes(dateString, source2Content)

source1Dict, lastWrittenSource1Wh = readInMemory('Source 1', source1Content, dateString, lastTargetMinutes, 0)
source2Dict, lastWrittenSource2Wh = readInMemory('Source 2', source2Content, dateString, lastTargetMinutes, 0)

while True:
    log('Sleeping for 5 minutes')
    time.sleep(300) # wait 5 minutes before checking again

    now = datetime.now()
    if now.hour < 5 or now.hour > 22: # only check between 5 and 23 hour
        log('Outside solar generation hours (5..23)')
        sys.exit('Exiting program to avoid possible memory leaks')

    timeString = minutesToTimeString(lastTargetMinutes)
    source1Content = getStatus('Source1', GET_PVOUTPUT_SOURCE1_GET_STATUS_URL, dateString, timeString)
    lastSource1Minutes = computeMinutes(dateString, source1Content)
    source1Dict = {}
    if lastSource1Minutes > lastTargetMinutes:
        source1Dict, nop1Wh = readInMemory('Source 1', source1Content, dateString, lastTargetMinutes, lastWrittenSource1Wh)
    elif now.hour != 22: # when after 22:00 if there are results, process them anyway, because other inverter might be sleeping
        continue # nothing to do

    source2Content = getStatus('Source2', GET_PVOUTPUT_SOURCE2_GET_STATUS_URL, dateString, timeString)
    lastSource2Minutes = computeMinutes(dateString, source2Content)
    source2Dict = {}
    if lastSource2Minutes > lastTargetMinutes:
        source2Dict, nop2Wh = readInMemory('Source 2', source2Content, dateString, lastTargetMinutes, lastWrittenSource2Wh)
    elif now.hour != 22: # when after 22:00 if there are results, process them anyway, because other inverter might be sleeping
        continue # nothing to do

    if lastSource1Minutes <= lastTargetMinutes and lastSource2Minutes <= lastTargetMinutes:
        continue # nothing to do

    log("Processing....")
    dataPointsCount = 0
    dataPointsStr = 'data='
    source1Keys = list(source1Dict.keys())
    source2Keys = list(source2Dict.keys())
    # Since python 3.7 the order is insertion, so the minimum of first entries and last entries can be computed
    
    len1 = len(source1Keys)
    len2 = len(source2Keys)
    if len1 > 0 and len2 > 0:
        fromMinutes = min(source1Keys[0], source2Keys[0])
        toMinutes = min(source1Keys[len1-1], source2Keys[len2-1])
    elif len1 > 0:
        fromMinutes = source1Keys[0]
        toMinutes = source1Keys[len1-1]
    else:
        fromMinutes = source2Keys[0]
        toMinutes = source2Keys[len2-1]

    while fromMinutes <= toMinutes:
        d = dateString
        t = minutesToTimeString(fromMinutes)
        wh = 0
        w = 0
        v = 0.0
        if fromMinutes in source1Dict:
            line1 = source1Dict[fromMinutes]
            #print('line1=[' + line1 + ']')
            d1, t1, whStr1, wStr1, nop1, nop2, temp1, vStr1 = line1.split(',')
            lastWrittenSource1Wh = int(whStr1)
            wh = lastWrittenSource1Wh
            w = int(wStr1)
            v = float(vStr1)    
        else:
            wh = lastWrittenSource1Wh

        if fromMinutes in source2Dict:
            line2 = source2Dict[fromMinutes]
            #print('line2=[' + line2 + ']')
            d2, t2, whStr2, wStr2, nop3, nop4, temp2, vStr2 = line2.split(',')
            lastWrittenSource2Wh = int(whStr2)
            wh += lastWrittenSource2Wh
            w += int(wStr2)
            v += float(vStr2)
        else:
            wh = lastWrittenSource2Wh

        if fromMinutes > lastTargetMinutes: # only write when AFTER last target time
            pvoutputString = d+','+t+','+str(wh)+','+str(w)+',,,,'+str(round(v))
            dataPointsCount += 1
            if dataPointsCount > 1:
                dataPointsStr += ';'
            dataPointsStr += pvoutputString
            if dataPointsCount >= 29:
                addBatchStatus(dataPointsCount, dataPointsStr)
                dataPointsStr = 'data='
                dataPointsCount = 0

        fromMinutes += 5 # next 5 minutes

    if dataPointsCount > 0:
        addBatchStatus(dataPointsCount, dataPointsStr)

    lastTargetMinutes = min(lastSource1Minutes, lastSource2Minutes)
