[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Combine PVOutput Systems
Simple Python3 script to combine two PVOutput Systems continously (normally once per 5 minutes) into a target PVOutput System.

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
Change in combine_two_pvoutput_systems.py the following lines with your above obtained secrets:
* PVOUTPUT_SOURCE1_API_KEY = 'xxxx'
* PVOUTPUT_SOURCE1_SYSTEM_ID = 'xxxx'
* PVOUTPUT_SOURCE2_API_KEY = 'xxxx'
* PVOUTPUT_SOURCE2_SYSTEM_ID = 'xxxx'
* PVOUTPUT_TARGET_API_KEY = 'xxxx'
* PVOUTPUT_TARGET_SYSTEM_ID = 'xxxx'

## Usage
### Windows 10
python combine_two_pvoutput_systems.py

### Raspberry pi
combine_two_pvoutput_systems.py script runs on my Raspberry pi Model B with 512 MB memory (yes, very old, from 2012) with Raspbian GNU/Linux 11 (bullseye).

### Raspberry pi Configuration
Steps:
* create a directory solis in your home directory
* copy pvoutput.sh and combine_two_pvoutput_systems.py in this solis directory
* change inside combine_two_pvoutput_systems.py the API_KEY and SYSTEM_ID secrets
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
20220803 14:06:04: GET Target   &d="20220803"&t="05:00"
20220803 14:06:05: Target   read_in_memory since: 05:00
20220803 14:06:05: Target   read_in_memory last values: written time=05:00, written wh=0, wh=14209, line=20220803,13:55,14209,4686,,,,391.0
20220803 14:06:05: Last Written target: 13:55
20220803 14:06:05: GET Source 1 &d="20220803"&t="13:55"
20220803 14:06:05: Source 1 read_in_memory since: 13:55
20220803 14:06:06: Source 1 read_in_memory last values: written time=13:55, written wh=7544, wh=7809, line=20220803,14:00,7809,3180,,,,237.5
20220803 14:06:06: GET Source 2 &d="20220803"&t="13:55"
20220803 14:06:06: Sleeping for 5 minutes
20220803 14:11:06: GET Source 1 &d="20220803"&t="13:55"
20220803 14:11:07: Source 1 read_in_memory since: 13:55
20220803 14:11:07: Source 1 read_in_memory last values: written time=13:55, written wh=7544, wh=8079, line=20220803,14:05,8079,3240,,,,237.5
20220803 14:11:07: GET Source 2 &d="20220803"&t="13:55"
20220803 14:11:08: Source 2 read_in_memory since: 13:55
Missing entry:
---> 20220803,13:55,6665,1530,,,,154.0
---> 20220803,14:05,6900,1520,,,,153.9
Prev : 20220803,13:55,6665,1530,,,,154.0
Added: 20220803,14:00,6782,1520,,,,153.9
Next : 20220803,14:05,6900,1520,,,,153.9

20220803 14:11:08: Source 2 read_in_memory last values: written time=13:55, written wh=6665, wh=6900, line=20220803,14:05,6900,1520,,,,153.9
20220803 14:11:08: Processing....
20220803 14:11:08: Target datapoints: 2
1: data=20220803,14:00,14591,4700,,,,391
2: 20220803,14:05,14979,4760,,,,391
20220803 14:11:08: Sleeping for 5 minutes
20220803 14:16:08: GET Source 1 &d="20220803"&t="14:05"
20220803 14:16:09: Source 1 read_in_memory since: 14:05
20220803 14:16:09: Source 1 read_in_memory last values: written time=14:05, written wh=8079, wh=8351, line=20220803,14:10,8351,3264,,,,237.4
20220803 14:16:09: GET Source 2 &d="20220803"&t="14:05"
20220803 14:16:10: Source 2 read_in_memory since: 14:05
20220803 14:16:10: Source 2 read_in_memory last values: written time=14:05, written wh=6900, wh=7025, line=20220803,14:10,7025,1510,,,,150.1
20220803 14:16:10: Processing....
20220803 14:16:10: Target datapoints: 1
1: data=20220803,14:10,15376,4774,,,,388
20220803 14:16:10: Sleeping for 5 minutes
20220803 14:21:10: GET Source 1 &d="20220803"&t="14:10"
20220803 14:21:10: Source 1 read_in_memory since: 14:10
20220803 14:21:11: Source 1 read_in_memory last values: written time=14:10, written wh=8351, wh=8625, line=20220803,14:15,8625,3288,,,,237.6
20220803 14:21:11: GET Source 2 &d="20220803"&t="14:10"
20220803 14:21:11: Source 2 read_in_memory since: 14:10
20220803 14:21:11: Source 2 read_in_memory last values: written time=14:10, written wh=7025, wh=7149, line=20220803,14:15,7149,1490,,,,150.4
20220803 14:21:11: Processing....
20220803 14:21:11: Target datapoints: 1
1: data=20220803,14:15,15774,4778,,,,388
20220803 14:21:11: Sleeping for 5 minutes
```

