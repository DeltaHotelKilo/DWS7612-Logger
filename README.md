# DWS7612-Logger
Reads and decodes SML messages of a DWS7612 electric meter. Optionally, stores the meter readings for Positive Active Energy (1.8.0) and Negative Active Energy (2.8.0) into a MySQL database.

## Hard- and Software Requirements
The software was tested on a Raspberry Pi 3 B+ with Debian 11 (Bullseye), MariaDB 10.5.23 and Python 3.5 installed.<br>
Additionally, you need the following hardware:<br>
- [DWS7612 Smart Meter](https://www.dzg.de/produkte/moderne-messeinrichtung#dvs76)
- [IR Smart-Meter-Interface](https://wiki.volkszaehler.org/hardware/controllers/ir-schreib-lesekopf-usb-ausgang) (or similar)

## Installation
The script can be executed manually (type: `python3 dws7612.py -h` for help), but it is designed to run as a service.

If you want the software to log your meter data into a <b>MySQL</b> database you have to setup the database and modify the configuration file accordingly.
To setup the database, you can just import the file `dws7612.sql` into your MySQL environment using e.g. 'phpMyAdmin', or similar.

If you want the data to be stored in a database with a different structure, you have to modify the function `_log_data` accordingly.

To install the software on e.g. a Raspberry Pi copy the repository to a local directory and complete the following steps:

edit and save the configuration file (see comments in the file):

    nano ./dws7612.cfg    

create a working directory and copy the corresponding files:

    sudo mkdir /usr/local/bin/dws7612
    sudo cp ./dws7612.py /usr/local/bin/dws7612/
    sudo cp ./dws7612.cfg /usr/local/bin/dws7612/

<b>Important:</b> if you want to install the software into a different directory as the one stated above, you have to modify the service file `dws7612.service` accordingly!

setup the service:

    sudo cp ./dws7612.service /etc/systemd/system
    sudo systemctl daemon-reload
    sudo systemctl enable dws7612.service
    sudo systemctl start dws7612.service

check the serivce is running:

    sudo systemctl status dws7612.service

the output should look somehow like this:

    pi@meterpi:~/pi/dws7612 $ sudo systemctl status dws7612.service
    * dws7612.service - DWS7612 - Electrical Meter Logger
       Loaded: loaded (/etc/systemd/system/dws7612.service; enabled; vendor preset: enabled)
       Active: active (running) since Mon 2024-02-12 15:19:05 CET; 3h 38min ago
     Main PID: 23008 (dws7612.py)
        Tasks: 2 (limit: 1595)
          CPU: 1min 14.923s
       CGroup: /system.slice/dws7612.service
               └─23008 /usr/bin/python3 -u /usr/local/bin/dws7612/dws7612.py

    Feb 12 15:19:06 meterpi dws7612.py[23008]: Copyright (©) 2024, Holger Kupke, License: GNU GPLv3
    Feb 12 15:19:06 meterpi dws7612.py[23008]: Config:  /usr/local/bin/dws7612/dws7612.cfg
    Feb 12 15:19:06 meterpi dws7612.py[23008]: Device:  /dev/ttyUSB0
    Feb 12 15:19:06 meterpi dws7612.py[23008]: Cycle:   60
    Feb 12 15:19:06 meterpi dws7612.py[23008]: Logging: enabled


