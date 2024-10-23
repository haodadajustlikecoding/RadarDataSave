#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：breath_detect 
@File    ：datasave_process.py
@IDE     ：PyCharm 
@Author  ：FDU_WICAS_HS
@Email   ：shuai.hao@iclegend.com
@Date    ：2023/7/21 10:58
@ReadMe  ：  用于保存数据
'''
import os
import scipy.io as sio
import numpy as np
import multiprocessing
from multiprocessing import Process
from multiprocessing import Queue

import scipy.io
import heapq
import matplotlib.pyplot as plt
import time

from Parameters import RangebinLen, buf_size

plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一（替换sans-serif字体）
plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
import datetime
import winsound
duration = 500  # 持续时间/ms
frequency = 500  # 频率/Hz

class dataSave_process(Process):
    def __init__(self,inputq,savepath):
        super().__init__()
        self.input_dataq = inputq
        self.savepath = savepath
        self.RangbinLen = RangebinLen
        # self.buf_size = self.RangbinLen * 4*4 +13 # 输出 rawCpx+ridx+dist+moveflag+ MTIabs+avgsumABS
        # self.buf_size = self.RangbinLen * 3*4 +13 + 4 * 6 # 输出 rawCpx+ridx+dist+moveflag+ MTIabs+各种呼吸频率的值
        self.buf_size = buf_size # 168 AI
        # self.one_chirp_bytesnum = self.RangbinLen * 4
        self.one_chirp_bytesnum = 13 * 4

        # self.buf_size = self.RangbinLen * 2*4 + 39 # rawCpx +ridx+dist+moveflag + breathFreq+Freq15+Freq50+15power+50power+wave+pauseflag

    def run(self) -> None:
        print('start coping with one chirp data')
        # self.dataSave_throughput_saveTXT(self.input_dataq,self.savepath)
        self.dataSave_throughput_saveTXT(self.input_dataq,self.savepath)

        # self.dataSave_throughput_BreathRate(self.input_dataq,self.savepath)
    def dataSave_throughput_move_exist_config(self,inq, save_path):
        dist_list = []
        ridx_list = []
        move_buffer_list = []
        exist_buffer_list = []
        exist_move_list = []
        data = []
        cnt = 0
        while True:
            if not inq.empty():
                tmp_check = inq.get()
                print(save_path[-24:-19], cnt)
                cnt += 1
                # 保存TXT文件
                txt_path = save_path + '.txt'

                with open(txt_path, 'a') as f:
                    for txt_save_idx in range(len(tmp_check)):
                        f.write(str(tmp_check[txt_save_idx]))
                        f.write(',')

                    f.write('\n')

                if cnt % (5 * 40) == 0:
                    winsound.Beep(frequency, duration)

                # # 保存 dat 文件
                # dat_path = save_path + '.dat'
                #
                # with open(dat_path,'a') as f1:
                #     for dat_save_idx in range(len(tmp_check)):
                #         f1.write(str(tmp_check[dat_save_idx]))
                #         f1.write(',')
                #     # f1.write(tmp_check)
                #
                #     f1.write('\n')

                cpx_value = np.zeros(10, dtype=np.complex64)
                if len(tmp_check) == self.buf_size:
                    cpx_value = np.zeros(10, dtype=np.complex64)
                    if tmp_check[0] == 0xF1 and tmp_check[1] == 0xF2 and tmp_check[2] == 0xF3 and tmp_check[3] == 0xF4 \
                            and tmp_check[-4] == 0xF5 and tmp_check[-3] == 0xF6 and tmp_check[-2] == 0xF7 and tmp_check[-1] == 0xF8:
                        tmp_check = tmp_check.astype(np.int32)
                        noise_floor = np.float64(np.int32(
                            tmp_check[4:self.one_chirp_bytesnum*2 + 4:4] + (tmp_check[5:self.one_chirp_bytesnum*2 + 4:4] << 8) + (tmp_check[6:self.one_chirp_bytesnum*2 + 4:4] << 16) + (
                                    tmp_check[7:self.one_chirp_bytesnum*2 + 4:4] << 24))) / 1e3
                        cpx_value = noise_floor[0::2] + noise_floor[1::2] * 1j
                        # print(cpx_value.shape,cpx_value)

                        ridx = tmp_check[self.one_chirp_bytesnum*2 + 4]
                        dist = np.uint32(tmp_check[self.one_chirp_bytesnum*2 + 6] + (tmp_check[self.one_chirp_bytesnum*2 + 7] << 8)) / 10
                        exist_move = tmp_check[self.one_chirp_bytesnum*2 + 8]
                        exist_buffer = np.float64(np.int32(
                            tmp_check[self.one_chirp_bytesnum*2 + 9:self.one_chirp_bytesnum*3 + 9:4] + (tmp_check[self.one_chirp_bytesnum*2 + 10:self.one_chirp_bytesnum*3 + 9:4] << 8) + (tmp_check[self.one_chirp_bytesnum*2 + 11:self.one_chirp_bytesnum*3 + 9:4] << 16) + (
                                    tmp_check[self.one_chirp_bytesnum*2 + 12:self.one_chirp_bytesnum*3 + 9:4] << 24))) / 1e3
                        move_buffer = np.float64(np.int32(
                            tmp_check[self.one_chirp_bytesnum*3 + 9:self.one_chirp_bytesnum*4 + 9:4] + (tmp_check[self.one_chirp_bytesnum*3 + 10:self.one_chirp_bytesnum*4 + 9:4] << 8) + (tmp_check[self.one_chirp_bytesnum*3 + 11:self.one_chirp_bytesnum*4 + 9:4] << 16) + (
                                    tmp_check[self.one_chirp_bytesnum*3 + 12:self.one_chirp_bytesnum*4 + 9:4] << 24))) / 1e3

                        print(ridx, dist, exist_buffer)
                        ridx_list.append(ridx)
                        dist_list.append(dist)
                        data.append(cpx_value)
                        exist_move_list.append(exist_move)
                        move_buffer_list.append(move_buffer)
                        exist_buffer_list.append(exist_buffer)

                        sio.savemat(save_path + '.mat',
                                    {"data_list": data,
                                     "ridx_list": ridx_list,
                                     "dist_list": dist_list,
                                     'move_flag_list': exist_move_list,
                                     'exist_buffer_list': exist_buffer_list,
                                     'move_buffer_list': move_buffer_list,
                                     })

                    else:
                        print(tmp_check[0], tmp_check[1], tmp_check[2], tmp_check[3], tmp_check[-4], tmp_check[-3],
                              tmp_check[-2], tmp_check[-1])
                else:
                    # pass
                    print(len(tmp_check))
                    print(tmp_check)

                    # plt.plot(np.abs(cpx_value_MTI))
                    # plt.plot([10] * 7)
                    #
                    # plt.title("cnt{}_ridx{}".format(cnt,ridx[-1]), fontsize=40, color="red")
                    # plt.draw()
                    # # plt.ylim([0, 30000])
                    # plt.ylim([0, 100])
                    # plt.pause(0.05)
                    # plt.clf()



            else:
                # print('accumulate step error')
                time.sleep(0.001)
    def dataSave_throughput_saveTXT(self, inq, save_path):

        cnt = 0
        while True:
            if not inq.empty():
                tmp_check = inq.get()
                print(save_path[-24:-19], cnt)
                cnt += 1
                # 保存TXT文件
                txt_path = save_path + '.txt'
                t = time.time()
                t = int(round(t * 1000))

                # if cnt % 5 *60 == 0 :
                #     winsound.Beep(frequency, duration)
                # print(datetime.datetime.fromtimestamp(t/1000))
                with open(txt_path, 'a') as f:
                    f.write(str(170)+','+str(t)+','+str(85)+',')
                    for txt_save_idx in range(len(tmp_check)):
                        f.write(str(tmp_check[txt_save_idx]))
                        f.write(',')
                    f.write('\n')
            else:
                # print('accumulate step error')
                time.sleep(0.001)

    def dataSave_throughput_BreathRate(self, inq, save_path):
        dist_list = []
        breath_phase_list = []
        breath_freq_list = []
        ridx_list = []
        move_flag_list = []
        breath_state_list = []
        fft15power_list = []
        fft50power_list = []
        breathrate15_list = []
        breathrate50_list = []
        data = []
        ridx = []
        dist = []
        exist_move = []
        data_mti_list = []

        cnt = 0
        while True:
            if not inq.empty():
                tmp_check = inq.get()
                print(save_path[-24:-19], cnt)
                cnt += 1
                # 保存TXT文件
                txt_path = save_path + '.txt'
                t = time.time()
                t = int(round(t * 1000))

                # if cnt % 5 *60 == 0 :
                #     winsound.Beep(frequency, duration)
                # print(datetime.datetime.fromtimestamp(t/1000))
                with open(txt_path, 'a') as f:
                    f.write(str(170)+','+str(t)+','+str(85)+',')
                    for txt_save_idx in range(len(tmp_check)):
                        f.write(str(tmp_check[txt_save_idx]))
                        f.write(',')

                    f.write('\n')
                cpx_value = np.zeros(10, dtype=np.complex64)
                tmp_check = np.frombuffer(tmp_check, dtype=np.uint8)
                if len(tmp_check) == self.buf_size:
                    cpx_value = np.zeros(10, dtype=np.complex64)
                    if tmp_check[0] == 0xF1 and tmp_check[1] == 0xF2 and tmp_check[2] == 0xF3 and tmp_check[3] == 0xF4 \
                            and tmp_check[-4] == 0xF5 and tmp_check[-3] == 0xF6 and tmp_check[-2] == 0xF7 and tmp_check[-1] == 0xF8:
                        tmp_check = tmp_check.astype(np.int32)
                        noise_floor = np.float64(np.int32(
                            tmp_check[4:self.one_chirp_bytesnum*2 + 4:4] + (tmp_check[5:self.one_chirp_bytesnum*2 + 4:4] << 8) + (tmp_check[6:self.one_chirp_bytesnum*2 + 4:4] << 16) + (
                                    tmp_check[7:self.one_chirp_bytesnum*2 + 4:4] << 24))) / 1e3
                        cpx_value = noise_floor[0::2] + noise_floor[1::2] * 1j
                        ridx = tmp_check[self.one_chirp_bytesnum*2 + 4]
                        dist = np.uint32(tmp_check[self.one_chirp_bytesnum*2 + 6] + (tmp_check[self.one_chirp_bytesnum*2 + 7] << 8)) / 10
                        exist_move = tmp_check[self.one_chirp_bytesnum*2 + 8]

                        # print(cpx_value.shape,cpx_value)
                        breathrate_arm = (np.int32(tmp_check[self.one_chirp_bytesnum*2 + 9] + (tmp_check[self.one_chirp_bytesnum*2 + 10] << 8) + (tmp_check[self.one_chirp_bytesnum*2 + 11] << 16) + (tmp_check[self.one_chirp_bytesnum*2 + 12] << 24)))/1e3
                        newBreathrate15s = np.float64(np.int32(tmp_check[self.one_chirp_bytesnum*2 + 13] + (tmp_check[self.one_chirp_bytesnum*2 + 14] << 8) + (tmp_check[self.one_chirp_bytesnum*2 + 15] << 16) + (tmp_check[self.one_chirp_bytesnum*2 + 16] << 24)))/1e3
                        newBreathrate50s = np.float64(np.int32(tmp_check[self.one_chirp_bytesnum*2 + 17] + (tmp_check[self.one_chirp_bytesnum*2 + 18] << 8) + (tmp_check[self.one_chirp_bytesnum*2 + 19] << 16) + (tmp_check[self.one_chirp_bytesnum*2 + 20] << 24))) / 1e3
                        fft15power = np.float64(np.uint32(tmp_check[self.one_chirp_bytesnum*2 + 21] + (tmp_check[self.one_chirp_bytesnum*2 + 22] << 8) + (tmp_check[self.one_chirp_bytesnum*2 + 23] << 16) + (tmp_check[self.one_chirp_bytesnum*2 + 24] << 24)))/1e3
                        fft50power = np.float64(np.uint32(tmp_check[self.one_chirp_bytesnum*2 + 25] + (tmp_check[self.one_chirp_bytesnum*2 + 26] << 8) + (tmp_check[self.one_chirp_bytesnum*2 + 27] << 16) + (tmp_check[self.one_chirp_bytesnum*2 + 28] << 24)))/1e3
                        arm_breath_phase = np.float64(np.int32(tmp_check[self.one_chirp_bytesnum*2 + 29] + (tmp_check[self.one_chirp_bytesnum*2 + 30] << 8) + (tmp_check[self.one_chirp_bytesnum*2 + 31] << 16) + (tmp_check[self.one_chirp_bytesnum*2 + 32] << 24))) / 1e7/np.pi*0.05
                        # arm_result = tmp_check[self.one_chirp_bytesnum*2 + 12]



                        data_mti_abs = np.float64(np.int32(
                            tmp_check[self.one_chirp_bytesnum*2 +33:self.one_chirp_bytesnum*3 + 33:4] + (tmp_check[self.one_chirp_bytesnum*2 +34:self.one_chirp_bytesnum*3 + 33:4] << 8) + (tmp_check[self.one_chirp_bytesnum*2 +35:self.one_chirp_bytesnum*3 + 33:4] << 16) + (
                                    tmp_check[self.one_chirp_bytesnum*2 +36:self.one_chirp_bytesnum*3 + 33:4] << 24))) / 1e3

                        print(ridx, dist, '体动情况',exist_move) # 体动监测在这个时候就不好用了，debug20241021，发现更改了chirp后的体动判断不太好用，于是想看看没有用网络之前的体动判断是不是准的，发现也不准
                        data.append(cpx_value)
                        ridx_list.append(ridx)
                        dist_list.append(dist)
                        move_flag_list.append(exist_move)

                        breath_freq_list.append(breathrate_arm)
                        breathrate15_list.append(newBreathrate15s)
                        breathrate50_list.append(newBreathrate50s)
                        fft15power_list.append(fft15power)
                        fft50power_list.append(fft50power)
                        breath_phase_list.append(arm_breath_phase)

                        data_mti_list.append(data_mti_abs)

                        sio.savemat(save_path+ '.mat',
                                     {"data_list": data,
                                      "ridx_list": ridx_list,
                                      "dist_list": dist_list,
                                      'move_flag_list': move_flag_list,
                                      'breath_freq_list': breath_freq_list,
                                      'breathrate15_list':breathrate15_list,
                                      'breathrate50_list':breathrate50_list,
                                      'fft15power_list': fft15power_list,
                                      'fft50power_list': fft50power_list,
                                      'breath_phase_list':breath_phase_list,
                                      'data_mti_list':data_mti_list
                                      })
                    else:
                        print(tmp_check[0], tmp_check[1], tmp_check[2], tmp_check[3], tmp_check[-4], tmp_check[-3],
                              tmp_check[-2], tmp_check[-1])
                else:
                    # pass
                    print(len(tmp_check))
                    print(tmp_check)



            else:
                # print('accumulate step error')
                time.sleep(0.001)
    def dataSave_throughput_AI(self, inq, save_path):
        IQData_list = []
        ridx_list = []
        dist_list = []
        data_mti_list = []
        data_AI_output = []
        one_chirp_bytesnum = 9*4
        featurenum = 20
        cnt = 0
        while True:
            if not inq.empty():
                tmp_check = inq.get()
                print(save_path[-24:-19], cnt)
                cnt += 1
                # 保存TXT文件
                txt_path = save_path + '.txt'
                t = time.time()
                t = int(round(t * 1000))

                # if cnt % 5 *60 == 0 :
                #     winsound.Beep(frequency, duration)
                # print(datetime.datetime.fromtimestamp(t/1000))
                tmp_check = np.frombuffer(tmp_check, dtype=np.uint8)

                with open(txt_path, 'a') as f:
                    f.write(str(170)+','+str(t)+','+str(85)+',')
                    for txt_save_idx in range(len(tmp_check)):
                        f.write(str(tmp_check[txt_save_idx]))
                        f.write(',')

                    f.write('\n')

                if len(tmp_check) == self.buf_size:
                    cpx_value = np.zeros(10, dtype=np.complex64)
                    if tmp_check[0] == 0xF1 and tmp_check[1] == 0xF2 and tmp_check[2] == 0xF3 and tmp_check[3] == 0xF4 \
                            and tmp_check[-4] == 0xF5 and tmp_check[-3] == 0xF6 and tmp_check[-2] == 0xF7 and tmp_check[-1] == 0xF8:
                        tmp_check = tmp_check.astype(np.int32)
                        noise_floor = np.float64(np.int32(
                            tmp_check[4:one_chirp_bytesnum * 2 + 4:4] + (
                                        tmp_check[5:one_chirp_bytesnum * 2 + 4:4] << 8) + (
                                        tmp_check[6:one_chirp_bytesnum * 2 + 4:4] << 16) + (
                                    tmp_check[7:one_chirp_bytesnum * 2 + 4:4] << 24))) / 1e3
                        cpx_value = noise_floor[0::2] + noise_floor[1::2] * 1j
                        ridx = tmp_check[one_chirp_bytesnum * 2 + 4]
                        sleepflag = tmp_check[one_chirp_bytesnum * 2 + 5]
                        dist = np.uint32(
                            tmp_check[one_chirp_bytesnum * 2 + 6] + (tmp_check[one_chirp_bytesnum * 2 + 7] << 8)) / 10
                        data_mti_abs = np.float64(np.int32(
                            tmp_check[one_chirp_bytesnum * 2 + 8:one_chirp_bytesnum * 3 + 8:4] + (
                                        tmp_check[one_chirp_bytesnum * 2 + 9:one_chirp_bytesnum * 3 + 8:4] << 8) + (
                                        tmp_check[one_chirp_bytesnum * 2 + 10:one_chirp_bytesnum * 3 + 8:4] << 16) + (
                                    tmp_check[one_chirp_bytesnum * 2 + 11:one_chirp_bytesnum * 3 + 8:4] << 24))) / 1e3
                        NetRaw = np.float64(np.int32(
                            tmp_check[one_chirp_bytesnum * 3 + 8:one_chirp_bytesnum * 3 + 32:4] + (
                                        tmp_check[one_chirp_bytesnum * 3 + 9:one_chirp_bytesnum * 3 + 32:4] << 8) + (
                                        tmp_check[one_chirp_bytesnum * 3 + 10:one_chirp_bytesnum * 3 + 32:4] << 16) + (
                                    tmp_check[one_chirp_bytesnum * 3 + 11:one_chirp_bytesnum * 3 + 32:4] << 24))) / 1e3
                        NetIpt = np.float64(np.int32(
                            tmp_check[one_chirp_bytesnum * 3 + 32:one_chirp_bytesnum * 3 + 32 + featurenum * 4:4] + (
                                        tmp_check[
                                        one_chirp_bytesnum * 3 + 33:one_chirp_bytesnum * 3 + 32 + featurenum * 4:4] << 8) + (
                                        tmp_check[
                                        one_chirp_bytesnum * 3 + 34:one_chirp_bytesnum * 3 + 32 + featurenum * 4:4] << 16) + (
                                    tmp_check[
                                    one_chirp_bytesnum * 3 + 35:one_chirp_bytesnum * 3 + 32 + featurenum * 4:4] << 24))) / 1e6
                        NetOpt = np.float64(np.int32(
                            tmp_check[one_chirp_bytesnum * 3 + 32 + featurenum * 4:-4:4] + (
                                        tmp_check[one_chirp_bytesnum * 3 + 32 + featurenum * 4 + 1:-4:4] << 8) + (
                                        tmp_check[one_chirp_bytesnum * 3 + 32 + featurenum * 4 + 2:-4:4] << 16) + (
                                    tmp_check[one_chirp_bytesnum * 3 + 32 + featurenum * 4 + 3:-4:4] << 24))) / 1e3

                        print(ridx, dist,'体动情况',NetRaw[5])

                        # print(ridx, dist, NetOpt)
                        # IQData_list.append(cpx_value)
                        # ridx_list.append(ridx)
                        # dist_list.append(dist)
                        # data_mti_list.append(data_mti_abs)
                        # data_AI_output.append(NetOpt)
                        #
                        # sio.savemat(save_path+ '.mat',
                        #              {"data_list": IQData_list,
                        #               "ridx_list": ridx_list,
                        #               "dist_list": dist_list,
                        #               'data_mti_list':data_mti_list,
                        #               'NetOutput':data_AI_output,
                        #               })
                    else:
                        print(tmp_check[0], tmp_check[1], tmp_check[2], tmp_check[3], tmp_check[-4], tmp_check[-3],
                              tmp_check[-2], tmp_check[-1])
                else:
                    # pass
                    print(len(tmp_check))
                    print(tmp_check)



            else:
                # print('accumulate step error')
                time.sleep(0.001)
    def dataSave_throughput_debugAI(self, inq, save_path):
        IQData_list = []
        ridx_list = []
        dist_list = []
        data_mti_list = []
        arm_BR_list = []
        data_AI_input = []

        cnt = 0
        while True:
            if not inq.empty():
                tmp_check = inq.get()
                print(save_path[-24:-19], cnt)
                cnt += 1
                # 保存TXT文件
                txt_path = save_path + '.txt'
                t = time.time()
                t = int(round(t * 1000))

                # if cnt % 5 *60 == 0 :
                #     winsound.Beep(frequency, duration)
                # print(datetime.datetime.fromtimestamp(t/1000))
                with open(txt_path, 'a') as f:
                    f.write(str(170)+','+str(t)+','+str(85)+',')
                    for txt_save_idx in range(len(tmp_check)):
                        f.write(str(tmp_check[txt_save_idx]))
                        f.write(',')

                    f.write('\n')
                if len(tmp_check) == self.buf_size:
                    cpx_value = np.zeros(10, dtype=np.complex64)
                    if tmp_check[0] == 0xF1 and tmp_check[1] == 0xF2 and tmp_check[2] == 0xF3 and tmp_check[3] == 0xF4 \
                            and tmp_check[-4] == 0xF5 and tmp_check[-3] == 0xF6 and tmp_check[-2] == 0xF7 and tmp_check[-1] == 0xF8:
                        tmp_check = tmp_check.astype(np.int32)
                        noise_floor = np.float64(np.int32(
                            tmp_check[4:self.one_chirp_bytesnum*2 + 4:4] + (tmp_check[5:self.one_chirp_bytesnum*2 + 4:4] << 8) + (tmp_check[6:self.one_chirp_bytesnum*2 + 4:4] << 16) + (
                                    tmp_check[7:self.one_chirp_bytesnum*2 + 4:4] << 24))) / 1e3
                        cpx_value = noise_floor[0::2] + noise_floor[1::2] * 1j
                        ridx = tmp_check[self.one_chirp_bytesnum*2 + 4]
                        dist = np.uint32(tmp_check[self.one_chirp_bytesnum*2 + 6] + (tmp_check[self.one_chirp_bytesnum*2 + 7] << 8)) / 10
                        data_mti_abs_targetRangbin = np.float64(np.uint32(tmp_check[self.one_chirp_bytesnum*2 + 8] + (tmp_check[self.one_chirp_bytesnum*2 + 9] << 8) + (tmp_check[self.one_chirp_bytesnum*2 + 10] << 16) + (tmp_check[self.one_chirp_bytesnum*2 + 11] << 24)))/1e3
                        arm_breath_phase = np.float64(np.int32(tmp_check[self.one_chirp_bytesnum*2 + 12] + (tmp_check[self.one_chirp_bytesnum*2 + 13] << 8) + (tmp_check[self.one_chirp_bytesnum*2 + 14] << 16) + (tmp_check[self.one_chirp_bytesnum*2 + 15] << 24))) / 1e6

                        NetIpt = np.float64(np.int32(
                            tmp_check[self.one_chirp_bytesnum*2 +16:-4:4] + (tmp_check[self.one_chirp_bytesnum*2 +17:-4:4] << 8) + (tmp_check[self.one_chirp_bytesnum*2 +18:-4:4] << 16) + (
                                    tmp_check[self.one_chirp_bytesnum*2 +19:-4:4] << 24))) / 1e3


                        IQData_list.append(cpx_value)
                        ridx_list.append(ridx)
                        dist_list.append(dist)
                        data_mti_list.append(data_mti_abs_targetRangbin)
                        arm_BR_list.append(arm_breath_phase)
                        data_AI_input.append(NetIpt)

                        sio.savemat(save_path+ '.mat',
                                     {"data_list": IQData_list,
                                      "ridx_list": ridx_list,
                                      "dist_list": dist_list,
                                      'data_mti_list':data_mti_list,
                                      'arm_BR_list':arm_BR_list,
                                      'NetOutput':data_AI_input,
                                      })
                    else:
                        print(tmp_check[0], tmp_check[1], tmp_check[2], tmp_check[3], tmp_check[-4], tmp_check[-3],
                              tmp_check[-2], tmp_check[-1])
                else:
                    # pass
                    print(len(tmp_check))
                    print(tmp_check)
            else:
                # print('accumulate step error')
                time.sleep(0.001)






