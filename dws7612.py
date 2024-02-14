#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

#########################################################################
#
# License: GNU General Public License 3
#
# Copyright (C) 2024  Holger Kupke
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
#########################################################################

"""Read and decode SML messages of a DWS7612.2 electric power meter.
   Store the meter readings for positive active energy (1.8.0) and
   negative active energy (2.8.0) in a MySQL database.

   Usage example:
     python3 dws7612.py [-1] [-v] [-n] [--nosql]

   Design goals:
    * Simplicity: no full SML decoder - DWS7612.2 specific format
    * Run as a service: see file 'dws7612.service'
    * Configurable: via 'dws7612.cfg'
    * MySQL integration: readings can be stored in a mysql database
    *

   References and remarks:
    * Helmut Schmidt (https://github.com/huirad).
      His scripts helped a lot decoding the SML messages and parts
      of this script have been derived from his ED300L-script.

    * Klaus J. Mueller (https://volkszaehler.org)
      I am using the vz-software for a very long time. The database
      structure and functionalty is still based on his software.
"""

__author__    = 'Holger Kupke'
__copyright__ = 'Copyright (\xa9) 2024, Holger Kupke, License: GNU GPLv3'
__version__   = '1.0.0'
__license__   = 'GNU General Public License 3'

#########################################################################
#
# Module-History
#  Date         Author            Reason
#  10-Feb-2024  Holger Kupke      v1.0.0 Initial version
#
#########################################################################

import os
import sys
import serial
import signal
import argparse
import threading
import subprocess
import configparser

from time import sleep, time_ns

import pymysql

########################### class definitions ###########################

class DWS7612Logger(threading.Thread):
  # Obis IDs
  _OID_180 = b'\x07\x01\x00\x01\x08\x00\xff' #Positive Active Energy
  _OID_280 = b'\x07\x01\x00\x02\x08\x00\xff' #Negative Active Energy

  def __init__(self, port, cycle, hostname='', username='', password='', database='', verbose=False):
    threading.Thread.__init__(self)

    # counters
    self._positive = 0.0
    self._negative = 0.0

    # USB port
    self._port = port

    # read cycle
    self._cycle = cycle


    self._mysql = False
    # mysql parameters
    self._hostname = hostname
    self._username = username
    self._password = password
    self._database = database

    if len(self._hostname) and \
       len(self._username) and \
       len(self._password) and \
       len(self._database):
      self._mysql = True

    # diverse
    self._verbose = verbose
    self._running = False
    self._run = True

  # public functions
  def get_positive(self):
    v = None
    for x in range(10):
      if self._running:
        break
      sleep(1)

    v = self._positive
    return v

  def get_negative(self):
    v = None
    for x in range(10):
      if self._running:
        break
      sleep(1)
    return v

  def stop(self):
    self._run = False

  # non-public functions
  def _log_data(self):
    if self._mysql:
      try:
        conn = pymysql.connect(host=self._hostname,
                               user=self._username,
                               password=self._password,
                               database=self._database,
                               cursorclass=pymysql.cursors.DictCursor)

        with conn:
          with conn.cursor() as cursor:
            ts = int(time_ns()/1000000)
            sql = "INSERT INTO `data` (`entity_id`, `time`, `value`) VALUES (%s, %s, %s)"
            cursor.execute(sql, ('2', str(ts), self._positive))
            sql = "INSERT INTO `data` (`entity_id`, `time`, `value`) VALUES (%s, %s, %s)"
            cursor.execute(sql, ('3', str(ts), self._negative))
            conn.commit()
      except (pymysql.Error) as e:
        print('MySQL Error: %s\n' % e)

  def _get_int(self, buffer, offset):
    result = None
    if (len(buffer)-offset) < 2:
      pass
    elif (buffer[offset] & 0xF0) == 0x50: # signed integer
      size = (buffer[offset] & 0x0F) # size including the 1-byte tag
      if (len(buffer)-offset) >= size:
        tmp = buffer[offset+1:offset+size]
        result = int.from_bytes(tmp, byteorder='big', signed=True)
    elif (buffer[offset] & 0xF0) == 0x60: # unsigned integer
      size = (buffer[offset] & 0x0F) # size including the 1-byte tag
      if (len(buffer)-offset) >= size:
        tmp = buffer[offset+1:offset+size]
        result = int.from_bytes(tmp, byteorder='big', signed=False)
    return result

  def _read_sml_message(self, ser):
    if self._verbose:
      print('Reading SML message...')

    start_seq = b'\x1b\x1b\x1b\x1b\x01\x01\x01\x01'
    stop_seq  = b'\x1b\x1b\x1b\x1b\x1a'

    msg = b''
    data = b''

    while True:
      # try reading until stop sequence
      data = ser.read_until(stop_seq)

      # reading failed, when there is no stop sequence
      stop_idx = data.find(stop_seq)
      if stop_idx < 0:
        break

      # read 3 more bytes (filler and crc)
      data += ser.read(3)

      # do again, if there is no start sequence
      start_idx = data.find(start_seq)
      if start_idx < 0:
        continue

      # stop sequence must be after start sequence
      if stop_idx > start_idx:
        msg = data[start_idx :(stop_idx + len(stop_seq) + 3)]
        break

    return msg

  def run(self):
    while self._run:
      telegram = b''
      data = b''

      try:
        ser = serial.Serial(self._port, 9600, timeout=3)
        msg = self._read_sml_message(ser)
        ser.close()

        if len(msg) and self._run:
          if self._verbose:
            print('Message length: %d' % len(msg))
            print(msg.hex())
            print()

          # decode positive active energy (1.8.0)
          offset = msg.find(self._OID_180)
          self._positive = 0.0
          if offset > 0:
            value = self._get_int(msg, offset+20)
            if value == None:
              value = 0
            self._positive = round((value/10000),3)
          if self._verbose:
            print('1.8.0: %s kWh' % str('%.3f' % (self._positive)).rjust(10))

          # decode negative active energy (2.8.0)
          offset = msg.find(self._OID_280)
          self._negative = 0.0
          if offset > 0:
            value = self._get_int(msg, offset+17)
            if value == None:
              value = 0
            self._negative = round((value/10000),3)
          if self._verbose:
            print('2.8.0: %s kWh' % str('%.3f' % (self._negative)).rjust(10))

          if self._verbose:
            print()

          # log the meter readings
          self._log_data()
        else:
          if self._run:
            print('Error: reading serial port (%s)' % (self._port))
            print()
      except serial.SerialException as e:
        print('Error: ' + str(e))
        if self._run == False:
          break
        sleep(2)
        continue

      # stop() has been call, so let's exit the thread
      if self._run == False:
        break

      # ensure the meter has at least been read once
      if self._running == False:
        self._running = True

      # sleep loop
      i = self._cycle * 100
      while i > 0:
        if self._run == False:
          break
        i -=1
        sleep(0.01)

class cfg:
  #section [General]
  cycle=''               #read cycle in seconds - default: 60
  #section [Meter]
  dport=''               #device port - default: /dev/ttyUSB0
  dname=''               #device name
  #section [MySQL]
  mysql_host=''          #host name or ip address
  mysql_user=''          #user name
  mysql_pwd=''           #user password
  mysql_db=''            #database name

########################### global functions ############################

def assert_python3():
  """ Assert that at least Python 3.5 is used
  """
  assert(sys.version_info.major == 3)
  assert(sys.version_info.minor >= 5)

def signalHandler(num, frame):
  if(num == signal.SIGINT):
    print('\r                    \r', end='')
    print('Interrupted by user.')

  sys.exit(0)

def read_cfg(nosql=False):
  cfg_file = os.path.dirname(os.path.abspath(__file__)) + '/dws7612.cfg'
  print('Config:  %s\n' %  cfg_file)

  parser = configparser.ConfigParser()
  parser.read(cfg_file)

  cfg.cycle = parser.getint('General', 'cycle', fallback=60)
  if cfg.cycle < 2:
    cfg.cycle = 60

  cfg.dport = parser.get('Meter', 'port', fallback='/dev/ttyUSB0')
  cfg.dname = parser.get('Meter', 'name', fallback='')

  global mysql_logging
  mysql_logging = False

  if nosql == False:
    cfg.mysql_host = parser.get('MySQL', 'hostname', fallback='')
    cfg.mysql_user = parser.get('MySQL', 'username', fallback='')
    cfg.mysql_pwd = parser.get('MySQL', 'password', fallback='')
    cfg.mysql_db = parser.get('MySQL', 'database', fallback='')

    if len(cfg.mysql_host) and \
       len(cfg.mysql_user) and \
       len(cfg.mysql_pwd) and \
       len(cfg.mysql_db):
      mysql_logging = True;

def get_port(device_name):
  port = ''
  command = 'dmesg | grep -i "' + device_name + '"'

  try:
    result = subprocess.check_output(command, shell=True, text=True)
    x = result.find('tty')
    if x:
      port='/dev/' + result[x:]
      x = port.find(' ')
      if x:
        port = port[:x]
  except Exception as ex:
    print(str(ex))

  return port

################################# main ##################################

def main():

  #setting up signal handlers
  signal.signal(signal.SIGINT, signalHandler)
  signal.signal(signal.SIGTERM, signalHandler)

  print('\033[1mDWS7612\033[0m - Electrical Meter Logger - v' + __version__)
  print('----------------------------------------------------')
  print(__copyright__ + '\n')

  global logger
  logger = None

  global args
  args = None

  parser = argparse.ArgumentParser()
  parser.add_argument('-1', '--once', action='store_true', help='Implies -v: Read the meter data just once and exit.')
  parser.add_argument('-v', '--verbose', action='store_true', help='Display runtime-information.')
  parser.add_argument('-n', '--nosql', action='store_true', help='Disable mysql logging.')
  args = parser.parse_args()

  if args.once:
    args.verbose = True

  read_cfg(args.nosql)
  if len(cfg.dname):
    cfg.dport = get_port(cfg.dname)

  print('Device:  ' + cfg.dport)
  print('Cycle:   ' + str(cfg.cycle))
  if args.nosql:
    print('Logging: \033[1;31mdisabled\033[0m\n')
  else:
    print('Logging: \033[1;32menabled\033[0m\n')

  if mysql_logging:
    logger = DWS7612Logger(cfg.dport, cfg.cycle, cfg.mysql_host, cfg.mysql_user, cfg.mysql_pwd, cfg.mysql_db, args.verbose)
  else:
    logger = DWS7612Logger(cfg.dport, cfg.cycle, verbose=args.verbose)
  logger.start()

  if args.once:
    logger.get_positive()
  else:
    while True:
      sleep(int(cfg.cycle))

if __name__ == '__main__':
  try:
    assert_python3()
    main()
  finally:
    if logger != None:
      if args.verbose:
        print("Stopping logger thread...", end="")

      logger.stop()
      logger.join()

      if args.verbose:
        print("\033[0;32mdone\033[0m.")

    print('Bye.')
