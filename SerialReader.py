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
        self.decoded_bytes = str(0)

    def connect(self):
        try:
            self.ser = serial.Serial('COM3', 9600, timeout=0)
            loop = True
        except Exception as e:
            loop = False
            logging.info(str(e))
        while loop:
            try:
                time.sleep(1)
                self.ser.write("get".encode())
                ser_bytes = self.ser.readline()
                self.decoded_bytes = str(ser_bytes[0:len(ser_bytes) - 2].decode("utf-8"))
                vs = self.decoded_bytes.split(",")
                for v in vs:
                    float(v)
                loop = False
            except Exception as e:
                logging.info(str(e))

    def read_serial(self):
        try:
            self.ser.write("get".encode())
            ser_bytes = self.ser.readline()
            temp = str(ser_bytes[0:len(ser_bytes) - 2].decode("utf-8"))
            vs = temp.split(",")
            for v in vs:
                float(v)
            self.decoded_bytes = temp
        except Exception as e:
            self.connect()
            logging.info(str(e))
        return str(self.decoded_bytes)
