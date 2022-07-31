[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Combine PVOutput Systems
Simple Python3 script to combine 2 PVOutput Systems continously (normally once per 5 minutes) into target PVOutput System.

PVOutput also includes possibilities for combining systems, but that needs a donation. With a donation you well get also other functionality, so make a choice if the donation features of PVOutput is a better route.

Notes
* you need 3 PVOutput accounts, for each system one.
* only between 5 and 23 hour data is fetched and combined into the target PVOutput
* the script will exit outside 5 and 23
* if one system is not updated anymore, the target PVOutput system will NOT be updated or the time must be after 22:00 hours (assumption tyhat one system has gone to sleep already)
* the script relies on Python version 3.7 and higher, using the ordered dictionary functionality.

## PVOutput
[PVOutput](https://pvoutput.org/) is a free online service for sharing and comparing photovoltaic solar panel output data. It provides both manual and automatic data uploading facilities.

Output data can be graphed, analysed and compared with other pvoutput contributors over various time periods. The ability to compare with similar systems within close proximity allows both short and longer term performance issues to be easily identified. While PVOutput is primarily focused on monitoring energy generation, it also provides equally capabable facilities to upload and monitor energy consumption data from various energy monitoring devices.

The python script requires multiple PVOutput API_KEY and SYSTEM_ID to function.
* Login in PVOutput and goto your Settings page for each account
* Select Enabled for API Access
* Click on New Key to generate your API key
* Make a note of your System Id
* Save your settings

## Configuration
Change in CombinePVOutputSystems.py the following lines with your above obtained secrets:
* PVOUTPUT_SOURCE1_API_KEY = 'xxxx'
* PVOUTPUT_SOURCE1_SYSTEM_ID = 'xxxx'
* PVOUTPUT_SOURCE2_API_KEY = 'xxxx'
* PVOUTPUT_SOURCE2_SYSTEM_ID = 'xxxx'
* PVOUTPUT_TARGET_API_KEY = 'xxxx'
* PVOUTPUT_TARGET_SYSTEM_ID = 'xxxx'

## Usage
### Windows 10
python CombinePVOutputSystems.py

### Raspberry pi
CombinePVOutputSystems.py script runs on my Raspberry pi Model B with 512 MB memory (yes, very old, from 2012) with Raspbian GNU/Linux 11 (bullseye).

### Raspberry pi Configuration
Steps:
* create a directory solis in your home directory
* copy pvoutput.sh and CombinePVOutputSystems.py in this solis directory
* change inside CombinePVOutputSystems.py the API_KEY and SYSTEM_ID secrets
* chmod + x pvoutput.sh
* add the following line in your crontab -e:

```
4 5 * * * ~/solis/pvoutput.sh > /dev/null
@reboot sleep 234 && ~/pvoutput/pvoutput.sh > /dev/null
```

### log files
Log files are written in the home subdirectory solis
* pvoutput.log containing the processing and data send to PVOutput (and maybe error messages)
* pvoutput.crontab.log containing the crontab output (normally it will say that solis.sh is running).

### Example output pvoutput.log

```
20220731 11:50:04: GET Target   &d="20220731"&t="05:00"
20220731 11:50:05: GET Source 1 &d="20220731"&t="05:00"
20220731 11:50:06: GET Source 2 &d="20220731"&t="05:00"
20220731 11:50:06: Source 1 readInMemory since: 11:40
20220731 11:50:06: Source 1 readInMemory last values: written time=11:40, written wh=2355, wh=2459, line=20220731,11:45,2459,1248,,,,233.5
20220731 11:50:06: Source 2 readInMemory since: 11:40
20220731 11:50:06: Source 2 readInMemory last values: written time=11:40, written wh=1240, wh=1360, line=20220731,11:50,1360,770,,,,163.3
20220731 11:50:06: Sleeping for 5 minutes
rick@raspberrypi:~/solis $ cat pvoutput.log
20220731 11:50:04: GET Target   &d="20220731"&t="05:00"
20220731 11:50:05: GET Source 1 &d="20220731"&t="05:00"
20220731 11:50:06: GET Source 2 &d="20220731"&t="05:00"
20220731 11:50:06: Source 1 readInMemory since: 11:40
20220731 11:50:06: Source 1 readInMemory last values: written time=11:40, written wh=2355, wh=2459, line=20220731,11:45,2459,1248,,,,233.5
20220731 11:50:06: Source 2 readInMemory since: 11:40
20220731 11:50:06: Source 2 readInMemory last values: written time=11:40, written wh=1240, wh=1360, line=20220731,11:50,1360,770,,,,163.3
20220731 11:50:06: Sleeping for 5 minutes
20220731 11:55:06: GET Source1 &d="20220731"&t="11:40"
20220731 11:55:07: Source 1 readInMemory since: 11:40
20220731 11:55:07: Source 1 readInMemory last values: written time=11:40, written wh=2355, wh=2577, line=20220731,11:50,2577,1416,,,,233.1
20220731 11:55:07: GET Source2 &d="20220731"&t="11:40"
20220731 11:55:08: Source 2 readInMemory since: 11:40
20220731 11:55:08: Source 2 readInMemory last values: written time=11:40, written wh=1240, wh=1397, line=20220731,11:55,1397,450,,,,159.1
20220731 11:55:08: Processing....
20220731 11:55:08: Target datapoints: 2
1: data=20220731,11:45,3755,1928,,,,397
2: 20220731,11:50,3937,2186,,,,396
20220731 11:55:08: POST Target
20220731 11:55:08: Sleeping for 5 minutes
20220731 12:00:08: GET Source1 &d="20220731"&t="11:50"
20220731 12:00:09: Source 1 readInMemory since: 11:50
20220731 12:00:09: Source 1 readInMemory last values: written time=11:50, written wh=2577, wh=2658, line=20220731,11:55,2658,972,,,,232.0
20220731 12:00:09: GET Source2 &d="20220731"&t="11:50"
20220731 12:00:09: Source 2 readInMemory since: 11:50
20220731 12:00:09: Source 2 readInMemory last values: written time=11:50, written wh=1360, wh=1439, line=20220731,12:00,1439,510,,,,166.8
20220731 12:00:09: Processing....
20220731 12:00:09: Target datapoints: 1
1: data=20220731,11:55,4055,1422,,,,391
20220731 12:00:09: POST Target
20220731 12:00:10: Sleeping for 5 minutes
20220731 12:05:10: GET Source1 &d="20220731"&t="11:55"
20220731 12:05:10: Source 1 readInMemory since: 11:55
20220731 12:05:10: Source 1 readInMemory last values: written time=11:55, written wh=2658, wh=2744, line=20220731,12:00,2744,1032,,,,233.2
20220731 12:05:10: GET Source2 &d="20220731"&t="11:55"
20220731 12:05:11: Source 2 readInMemory since: 11:55
20220731 12:05:11: Source 2 readInMemory last values: written time=11:55, written wh=1397, wh=1494, line=20220731,12:05,1494,670,,,,163.1
20220731 12:05:11: Processing....
20220731 12:05:11: Target datapoints: 1
1: data=20220731,12:00,4183,1542,,,,400
20220731 12:05:11: POST Target
20220731 12:05:11: Sleeping for 5 minutes
20220731 12:10:11: GET Source1 &d="20220731"&t="12:00"
20220731 12:10:12: Source 1 readInMemory since: 12:00
20220731 12:10:12: Source 1 readInMemory last values: written time=12:00, written wh=2744, wh=2855, line=20220731,12:05,2855,1332,,,,232.9
20220731 12:10:12: GET Source2 &d="20220731"&t="12:00"
20220731 12:10:13: Source 2 readInMemory since: 12:00
20220731 12:10:13: Source 2 readInMemory last values: written time=12:00, written wh=1439, wh=1544, line=20220731,12:10,1544,610,,,,167.2
20220731 12:10:13: Processing....
20220731 12:10:13: Target datapoints: 1
1: data=20220731,12:05,4349,2002,,,,396
20220731 12:10:13: POST Target
20220731 12:10:14: Sleeping for 5 minutes
20220731 12:15:14: GET Source1 &d="20220731"&t="12:05"
20220731 12:15:14: Source 1 readInMemory since: 12:05
20220731 12:15:14: Source 1 readInMemory last values: written time=12:05, written wh=2855, wh=2959, line=20220731,12:10,2959,1248,,,,232.0
20220731 12:15:14: GET Source2 &d="20220731"&t="12:05"
20220731 12:15:15: Source 2 readInMemory since: 12:05
20220731 12:15:15: Source 2 readInMemory last values: written time=12:05, written wh=1494, wh=1585, line=20220731,12:15,1585,500,,,,167.0
20220731 12:15:15: Processing....
20220731 12:15:15: Target datapoints: 1
1: data=20220731,12:10,4503,1858,,,,399
20220731 12:15:15: POST Target
20220731 12:15:16: Sleeping for 5 minutes
```

