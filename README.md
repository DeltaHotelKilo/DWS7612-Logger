# DWS7612-Logger
Reads and decodes SML messages of a DWS7612 electric meter. Optionally, stores the meter readings for Positive Active Energy (1.8.0) and Negative Active Energy (2.8.0) into a MySQL database.

Hard- and Software Requirements
-------------------------------
The script was tested on a Raspberry Pi 3 B+ with Debian Bullseye, MariaDB 10.5.23 and Python 3.5 installed.<br>
Additionally, you need the following hardware:<br>
- [DWS7612 Smart Meter](https://www.dzg.de/produkte/moderne-messeinrichtung#dvs76)
- [IR Smart-Meter-Interface](https://wiki.volkszaehler.org/hardware/controllers/ir-schreib-lesekopf-usb-ausgang) (as an example)

Installation
------------
This script can be executed manually (type "python3 dws7612.py -h" for help) but is designed to run as a service.

To install the software on e.g. a Raspberry Pi copy the repository to a local directory and complete the following steps:

    # create a directory and copy files:
    sudo mkdir /usr/local/bin/dws7612
    sudo cp ./dws7612.py /usr/local/bin/dws7612
    sudo cp ./dws7612.cfg /usr/local/bin/dws7612

    # set up the service:
    sudo cp ./dws7612.service /etc/systemd/system
    sudo systemctl daemon-reload
    sudo systemctl enable dws7612.service
    sudo systemctl start dws7612.service

    # check the serivce is running:
    sudo systemctl status dws7612.service

    # 

