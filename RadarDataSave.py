#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：breath_detect
@File ：RecieveCpxData_0320.py
@IDE  ：PyCharm
@Author ：
@Date ：2023/3/20 14:23
@File Brief:
"""
import datetime
import os

from serial.tools import list_ports
from multiprocessing import Queue
from datasave_process import dataSave_process
from rxUSB_process import *

# Data saved here
dsp_save_path = "./Data/{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S" ))
# os.makedirs(dsp_save_path, exist_ok=True)


if __name__ == "__main__":
    # buf_size = 2 * 4 * 7 + 8 + 4 + 1 + 4 + 1 + 4
    # buf_size = 2 * 4 * 7 + 8 +4

    # 视频保存线程
    # camera_video_savepath = dsp_save_path + '/camera_video.avi'
    # camera_cap = camera_videowriter_process(camera_video_savepath, 640, 480, 24)
    # camera_cap.start()

    # hkh传感器保存线程
    # hkh_data_save_path = dsp_save_path + '/hkh_sensor_'+time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.txt'
    # hkh_sensor_thread = HKH_sensor_saveDATA('AUTO',hkh_data_save_path,50)
    # hkh_sensor_thread.start() 

    # 找多个com口
    portlsit = list(serial.tools.list_ports.comports())

    port_com = []
    portname = []
    firmware_base = []
    for port in portlsit:
        num = len(portlsit)
        if num == 0:
            print('没有找到任何串口')
        else:
            print(port.description)
            if port.description[:12] == 'Silicon Labs' or port.description[:10] == 'USB Serial'and len(port.description) > 6:
                port_dispath_COM = port.description.split('(')[-1].split(')')[-2]
                print(port_dispath_COM)
                print(firmware_base)
                if port_dispath_COM != 'COM10':
                    portname.append(port_dispath_COM)
                    firmware_base.append(str(port.description[:3]))

    print('Current Serial Name : ' , portname)
    print(len(portname))
    if len(portname) == 2:
        print('datasave')
        rq1 = Queue(20)
        rq2 = Queue(20)
        rx_thread1 = rxUSB_process(portname[0],rq1)
        rx_thread2 = rxUSB_process(portname[1],rq2)
        os.makedirs(dsp_save_path+ '/data_'+str(portname[0]) + '_' + firmware_base[0],exist_ok=True)
        os.makedirs(dsp_save_path+ '/data_'+str(portname[1])+ '_' + firmware_base[1],exist_ok=True)

        savepath1 = dsp_save_path+ '/data_'+str(portname[0])+'_'+ firmware_base[0]+'/data_'+str(portname[0])+ '_'  +time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        savepath2 = dsp_save_path+ '/data_'+str(portname[1])+'_'+ firmware_base[1]+'/data_'+str(portname[1])+ '_' +time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        save_thread1 = dataSave_process(rq1,savepath1)
        save_thread2 = dataSave_process(rq2,savepath2)

        rx_thread1.start()
        rx_thread2.start()
        save_thread1.start()
        save_thread2.start()
    elif len(portname) == 1:
        rq1 = Queue(20)
        rx_thread1 = rxUSB_process(portname[0],rq1)
        savepath1 = dsp_save_path+ '/data_'+str(portname[0])+'_' +time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        save_thread1 = dataSave_process(rq1,savepath1)

        rx_thread1.start()
        time.sleep(0.01)
        save_thread1.start()


