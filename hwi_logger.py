# tanks dataindustry from hwinfo forum https://www.hwinfo.com/forum/threads/python-code-for-fetch-data-from-hwinfo.7247/
# for struct and example of read shared memory from hwinfo

import struct
import time
import psutil
import sys
import logging
import requests
import json

from multiprocessing import shared_memory
from construct import Struct, Int32un, Long

from SerialReader import SerialReader

api_url = "http://192.168.15.85:8088/api/v1/dados"

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

serial = SerialReader(file_dir)
serial.connect()

loop = True
while loop:
    try:
        cabecalho = ""
        informacoes = ""
        for index in range(sensor_element.dwNumReadingElements):
            if index == 0:
                cabecalho += "Date time,Temperature,"
                informacoes += time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()) + ","
                informacoes += serial.read_serial() + ","
            reading = reading_element_struct.unpack(memory.buf[offset + index * length: offset + (index + 1) * length])
            cabecalho += str(reading[4].replace(b'\00', b'').decode('utf-8')) + " " + str(
                reading[5].replace(b'\00', b'').decode('mbcs')) + ","
            informacoes += str(reading[6]) + ","
        todo = {"cabecalho": cabecalho, "informacoes": informacoes}
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(api_url, data=json.dumps(todo), headers=headers)
        except Exception as ex:
            logging.error(str(e))
        time.sleep(1)
    except Exception as e:
        logging.info("hwi_logger stop")
        logging.error(str(e))
        loop = False
