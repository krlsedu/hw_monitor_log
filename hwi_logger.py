# tanks dataindustry from hwinfo forum https://www.hwinfo.com/forum/threads/python-code-for-fetch-data-from-hwinfo.7247/
# for struct and example of read shared memory from hwinfo

import struct
import time
import psutil
import sys
import logging

from multiprocessing import shared_memory
from construct import Struct, Int32un, Long

from SerialReader import SerialReader

try:
    file_dir = sys.argv[1]
except IndexError:
    file_dir = ""

logging.basicConfig(filename=file_dir + "monitoring.log",
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')
logging.info("Started")

while "HWiNFO64.exe" not in (p.name() for p in psutil.process_iter()):
    logging.info("Waiting forHWiNFO64.exe")
    time.sleep(1)

loop = True
while loop:
    try:
        memory = shared_memory.SharedMemory('Global\\HWiNFO_SENS_SM2')
        logging.info("Successful read Global\\HWiNFO_SENS_SM2")
        loop = False
    except Exception:
        logging.info("Can't read Global\\HWiNFO_SENS_SM2")
        time.sleep(1)

sensor_element_struct = Struct(
    'dwSignature' / Int32un,
    'dwVersion' / Int32un,
    'dwRevision' / Int32un,
    'poll_time' / Long,
    'dwOffsetOfSensorSection' / Int32un,
    'dwSizeOfSensorElement' / Int32un,
    'dwNumSensorElements' / Int32un,
    'dwOffsetOfReadingSection' / Int32un,
    'dwSizeOfReadingElement' / Int32un,
    'dwNumReadingElements' / Int32un,
)

sensor_element = sensor_element_struct.parse(memory.buf[0:Struct.sizeof(sensor_element_struct)])

fmt = '=III128s128s16sdddd'

reading_element_struct = struct.Struct(fmt)
offset = sensor_element.dwOffsetOfReadingSection
length = sensor_element.dwSizeOfReadingElement

try:
    logging.info("Opening file " + file_dir + "monitoring.csv")
    f = open(file_dir + "monitoring.csv", "x")
    logging.info("file " + file_dir + "monitoring.csv" + " created")
    for index in range(sensor_element.dwNumReadingElements):
        if index == 0:
            f.write("Date time,")
        reading = reading_element_struct.unpack(memory.buf[offset + index * length: offset + (index + 1) * length])
        f.write(
            str(reading[4].replace(b'\00', b'').decode('utf-8')) +
            " " + str(reading[5].replace(b'\00', b'').decode('mbcs')) +
            ",")
    f.write("Temperature,")
    f.write("\n")
    f.close()
except Exception:
    logging.info("file " + file_dir + "monitoring.csv" + " exists")

f = open(file_dir + "monitoring.csv", "a")
logging.info("file " + file_dir + "monitoring.csv" + " opened")

serial = SerialReader(file_dir)
serial.connect()

loop = True
while loop:
    try:
        for index in range(sensor_element.dwNumReadingElements):
            if index == 0:
                f.write(time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()) + ",")
            reading = reading_element_struct.unpack(memory.buf[offset + index * length: offset + (index + 1) * length])
            f.write(str(reading[6]) + ",")

        f.write(serial.read_serial() + ",")
        time.sleep(1)
        f.write("\n")
    except Exception as e:
        logging.info("hwi_logger stop")
        logging.info(str(e))
        loop = False

f.close()
