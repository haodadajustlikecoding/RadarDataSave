#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：RadarDataSave
@File    ：Parameters.py
@IDE     ：PyCharm 
@Author  ：FDU_WICAS_HS
@Email   ：shuai.hao@iclegend.com
@Date    ：2024/10/23 16:32
@ReadMe  ：  
'''
import numpy as np
import os, time, sys
import scipy.io as sio
import matplotlib.pyplot as plt
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
import signal

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal


if 1:#__name__ == '__main__':
    COM_Baudrate = 256000 # 256000
    RangebinLen = 13
    # buf_size = 2 * 4 * 7 + 8 + 4 + 1 + 4 + 1 + 4
    # buf_size = 2 * 4 * 7 + 8 +4
    # buf_size = 2 * 4 * 7 + 8 + 4 + 1
    # buf_size = 18 # 上位机
    # buf_size = 2 * 4 * 7 * 2 + 8 + 4 + 1 # 透传 raw + mti
    # buf_size = 2 * 4 * 7  + 27  + 4 + 8# 透传 raw  debug+嵌入式计算的呼吸频率
    # buf_size = 2 * 4 * 7  + 2*4*7+8+5# 透传 raw  +7个rangbin 的mti非相干累积能量值大小，包括人在和人运动判断的
    # buf_size = RangebinLen*16+13
    # buf_size = RangebinLen*12+13+4*6

    # buf_size = 168 #for AI 9rangbin IQ+MTI+ridx+dist+10Net1+2Net2
    # buf_size = 132 #for debug 9rangbin IQ+MTI+ridx+dist+10Net1+2Net2
    buf_size = 272 # 300-4*7
    # buf_size = 74 # 300-4*7
    AAhead = b'\xAA'
    tail55 = b'\x55'
    FRAME_HEAD = np.array((241,242,243,244))
    FRAME_TAIL = np.array((245,246,247,248))
