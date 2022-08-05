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
20220805 08:15:06: Target   read_in_memory since 05:00: written=05:00, written wh=0, wh=152, line=20220805,08:05,152,294,,,,410.0
20220805 08:15:06: Last Written target: 08:05
20220805 08:15:06: Source 1 read_in_memory since 08:05: written=08:05, written wh=107, wh=124, line=20220805,08:10,124,204,,,,234.4
20220805 08:15:07: Source 2 read_in_memory since 08:05: written=08:05, written wh=45, wh=53, line=20220805,08:10,53,100,,,,175.6
20220805 08:15:07: Sleeping for 5 minutes
20220805 08:20:08: Source 1 read_in_memory since 08:05: written=08:05, written wh=107, wh=141, line=20220805,08:15,141,204,,,,234.6
20220805 08:20:08: Source 2 read_in_memory since 08:05: written=08:05, written wh=45, wh=62, line=20220805,08:15,62,110,,,,179.6
20220805 08:20:08: Target datapoints: 2
1: data=20220805,08:10,177,304,,,,410
2: 20220805,08:15,203,314,,,,414
20220805 08:25:09: Source 1 read_in_memory since 08:15: written=08:15, written wh=141, wh=161, line=20220805,08:20,161,240,,,,234.8
20220805 08:25:10: Source 2 read_in_memory since 08:15: written=08:15, written wh=62, wh=71, line=20220805,08:20,71,110,,,,179.5
20220805 08:25:10: Target datapoints: 1
1: data=20220805,08:20,232,350,,,,414
20220805 08:30:11: Source 1 read_in_memory since 08:20: written=08:20, written wh=161, wh=178, line=20220805,08:25,178,204,,,,234.3
20220805 08:30:12: Source 2 read_in_memory since 08:20: written=08:20, written wh=71, wh=100, line=20220805,08:25,100,130,,,,179.6
20220805 08:30:12: Target datapoints: 1
1: data=20220805,08:25,278,334,,,,414
20220805 08:35:13: Source 1 read_in_memory since 08:25: written=08:25, written wh=178, wh=196, line=20220805,08:30,196,216,,,,234.0
20220805 08:35:14: Source 2 read_in_memory since 08:25: written=08:25, written wh=100, wh=107, line=20220805,08:30,107,90,,,,167.6
20220805 08:35:14: Target datapoints: 1
1: data=20220805,08:30,303,306,,,,402
```

