import struct
import time
import psutil

import sys

try:
    file_dir = sys.argv[1]
except IndexError:
    file_dir = "log.csv"

from multiprocessing import shared_memory
from construct import Struct, Int32un, Long

while "HWiNFO64.exe" not in (p.name() for p in psutil.process_iter()):
    print("Waiting forHWiNFO64.exe")
    time.sleep(1)
loop = True
while loop:
    try:
        memory = shared_memory.SharedMemory('Global\\HWiNFO_SENS_SM2')
        loop = False
    except Exception:
        print("Can't read Global\\HWiNFO_SENS_SM2")
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
    f = open(file_dir, "x")
    for index in range(sensor_element.dwNumReadingElements):
        if index == 0:
            f.write("Date time,")
        reading = reading_element_struct.unpack(memory.buf[offset + index * length: offset + (index + 1) * length])
        f.write(
            str(reading[4].replace(b'\00', b'').decode('utf-8')) +
            " " + str(reading[5].replace(b'\00', b'').decode('mbcs')) +
            ",")
    f.write("\n")
    f.close()
except Exception:
    print("File exists")

f = open(file_dir, "a")

loop = True
while loop:
    try:
        for index in range(sensor_element.dwNumReadingElements):
            if index == 0:
                f.write(time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()) + ",")
            reading = reading_element_struct.unpack(memory.buf[offset + index * length: offset + (index + 1) * length])
            f.write(str(reading[6]) + ",")
        time.sleep(1)
        f.write("\n")
    except Exception:
        loop = False

f.close()
