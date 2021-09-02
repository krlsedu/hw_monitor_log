import serial
import logging
import time


class SerialReader:
    def __init__(self, file_dir):
        logging.basicConfig(filename=file_dir + "monitoring.log",
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S')
        self.ser = None
        self.decoded_bytes = float(0)

    def connect(self):
        try:
            self.ser = serial.Serial('COM4', 9600, timeout=0)
            loop = True
        except Exception as e:
            loop = False
            logging.info(str(e))
        while loop:
            try:
                ser_bytes = self.ser.readline()
                time.sleep(1)
                self.decoded_bytes = float(ser_bytes[0:len(ser_bytes) - 2].decode("utf-8"))
                loop = False
            except Exception as e:
                logging.info(str(e))

    def read_serial(self):
        try:
            ser_bytes = self.ser.readline()
            self.decoded_bytes = float(ser_bytes[0:len(ser_bytes) - 2].decode("utf-8"))
        except Exception as e:
            self.connect()
            logging.info(str(e))
        return str(self.decoded_bytes)
