#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：breath_detect 
@File    ：rxUSB_process.py
@IDE     ：PyCharm 
@Author  ：FDU_WICAS_HS
@Email   ：shuai.hao@iclegend.com
@Date    ：2023/7/21 10:29
@ReadMe  ：  
'''
from Parameters import COM_Baudrate, buf_size, FRAME_HEAD, FRAME_TAIL

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：08_DSPTEST_ON_PYTHON 
@File ：RecieveCpxData_0320.py
@IDE  ：PyCharm 
@Author ：feng.liu@iclegend.com
@Date ：2023/3/20 14:23 
@File Brief:
"""
import serial
import serial.tools.list_ports
import numpy as np
from multiprocessing import Process
import time

debug_show_qst = 1

class rxUSB_process(Process):
    def __init__(self, client, q):
        Process.__init__(self)
        self.client = client
        self.q = q

    def run(self):
        print("  Start rxUSB_thread. Client:", self.client)
        # rx_103_openBootMode(self.client, self.q,1)
        rxread_1byte(self.client, self.q)
        print("  Stop rxUSB_thread：Client error.")


# Receive data from usb COM port.
def rx_usb_auto(COM_NUM, rxQ):
    COM_Name = COM_NUM # 'AUTO'
    ser = serial.Serial()
    ser.baudrate = COM_Baudrate
    ser.port = COM_Name
    # ser.timeout = 2
    ser.timeout = 0
    if ser.is_open:
        ser.close()
    if ser.port != 'AUTO':
        try:
            ser.open()
        except Exception as e:
            print("     **ERROR**: USB COM port open FAIL.",e)
            return
    else:  # auto detect COM port
        ports_list = list(serial.tools.list_ports.comports())
        for port in ports_list:
            if port.description[:12] == 'Silicon Labs' and len(port.description) > 6:
                print(port.description,"#####################")
                port_name = port.description.split('(')[-1].split(')')[-2] # port_name = 'COM' + str(n)
                ser.port = port_name
                try:
                    ser.open()
                    if ser.is_open:
                        break
                except Exception as e:
                    print(e)
        if not ser.is_open:
            print("     **ERROR**: USB COM port open FAIL.")
            return
    if ser.is_open:
        print("     --USB COM port open success. ---",ser.port)
        # start up ignore period
        time.sleep(0)
        ser.reset_input_buffer()
        print("     --Receiving data...")

    print("     --Receiving data...")


    try:
        while True:  # USB COM data receiving
            rx_data = ser.read(buf_size)
            while rxQ.full():
                time.sleep(0.01)
                if debug_show_qst:
                    print("rxQ full")
            if len(rx_data) == 0:
                time.sleep(0.001)
            else:
                rxQ.put(rx_data)
                # print(len(rx_data))
    except Exception as e:
        print("    --Error receiving data.")
        print(e)


def rx_usb(COM_NUM, rxQ):
    COM_Name = COM_NUM # 'AUTO'
    ser = serial.Serial()
    ser.baudrate = COM_Baudrate
    ser.port = COM_Name
    ser.timeout = 0.21
    # ser.timeout = 0
    if ser.is_open:
        ser.close()

    try:
        ser.open()
    except Exception as e:
        print(e)
    if not ser.is_open:
        print("     **ERROR**: USB COM port open FAIL.")
        return
    if ser.is_open:
        print("     --USB COM port open success. ---",ser.port)
        # start up ignore period
        time.sleep(0.1)
        ser.reset_input_buffer()
        print("     --Receiving data...")

    print("     --Receiving data...")
    # buffer = bytearray()

    try:
        while True:  # USB COM data receiving
            # print(COM_NUM)

            time_start = time.time()
            rx_data = ser.read(buf_size)

            if rx_data == b'': #
                print('no Data')
                continue
            tmp_check = np.frombuffer(rx_data, dtype=np.uint8)
            while rxQ.full():
                time.sleep(0.01)
                if debug_show_qst:
                    print("rxQ full")
            rxQ.put(tmp_check)
            print('消耗时间', time.time() - time_start)
            # print(len(rx_data))

            # buffer.extend(rx_data)
            # start_index = buffer.find(b'\xAA')



    except Exception as e:
        print("    --Error receiving data.")
        print(e)

def rxread_1byte(COM_NUM, rxQ):
    frame_header = bytearray(list(FRAME_HEAD))
    frame_footer = bytearray(list(FRAME_TAIL))

    COM_Name = COM_NUM # 'AUTO'
    ser = serial.Serial()
    ser.baudrate = 256000
    ser.port = COM_Name
    ser.timeout = 2
    # ser.timeout = 0
    if ser.is_open:
        ser.close()

    try:
        ser.open()
    except Exception as e:
        print(e)
    if not ser.is_open:
        print("     **ERROR**: USB COM port open FAIL.")
        return
    if ser.is_open:
        print("     --USB COM port open success. ---",ser.port)
        # start up ignore period
        time.sleep(0.1)
        ser.reset_input_buffer()
        print("     --Receiving data...")

    print("     --Receiving data...")

    try:
        one_frameData = bytearray()
        receiveflag = 0
        while True:  # USB COM data receiving
            time_start = time.time()
            rx_data = ser.read(100)  # 每次读取100个字节

            if rx_data == b'':
                print('no Data')
                continue
            one_frameData.extend(rx_data)
            # print(one_frameData)
            # one_frameData.extend(np.frombuffer(rx_data, dtype=np.uint8))  # 将读取的数据添加到帧数据中
            # print(np.frombuffer(rx_data, dtype=np.uint8))

            # 检查帧头和帧尾
            while receiveflag == 0:
                header_index = one_frameData.find(frame_header)  # 查找帧头
                # print(header_index)
                if header_index != -1:
                    receiveflag = 1
                    # 截取帧头后的有效数据
                    one_frameData = one_frameData[header_index:]  # 从找到的帧头开始数据
                    break  # 找到帧头后跳出循环
                else:
                    break  # 如果没有找到帧头，则跳出内循环

            if receiveflag == 1:
                # 检查是否有完整的帧（包含尾部）
                if len(one_frameData) >= buf_size :
                    if one_frameData[buf_size-4:buf_size] == frame_footer:
                        # 找到完整的一帧数据
                        tmp_check = one_frameData[:buf_size]  # 取出缓冲区大小的数据
                        one_frameData = one_frameData[buf_size:]  # 剩下的数据保留在帧数据中
                        while rxQ.full():
                            time.sleep(0.01)
                            if debug_show_qst:
                                print("rxQ full")
                        # print('帧数据长度',len(tmp_check))
                        rxQ.put(tmp_check)  # 将数据放入队列
                        print('消耗时间', time.time() - time_start)
                        receiveflag = 0  # 重置接收标志
    except Exception as e:
        print("    --Error receiving data.")
        print(e)
