# DWS7612-Logger
Reads and decodes SML messages of a DWS7612 electric meter. Optionally, stores the meter readings for Positive Active Energy (1.8.0) and Negative Active Energy (2.8.0) into a MySQL database.

Hard- and Software Requirements
-------------------------------
The script was tested on a Raspberry Pi 3 B+ with Debian Bullseye and Python 3.5 installed.<br>
You need an optical smart meter interface with e.g. a USB connector.<br>
- [IR Smart-Meter-Interface](https://wiki.volkszaehler.org/hardware/controllers/ir-schreib-lesekopf-usb-ausgang)

