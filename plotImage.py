# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 14:17:20 2015

@author: jiayi
"""
import numpy as np
import matplotlib.pylab as plt
def plotCntTimes(result2d,result3d):
    plt.figure(figsize=(8,4))
    plt.plot(np.arange(result2d.shape[0]),result2d,label="2D Panorama",color="red")
    plt.plot(np.arange(result3d.shape[0]),result3d,"b--",label="3D Panorama")
    plt.xlabel("pixel resolution")
    plt.ylabel("pixel count")
    plt.legend()
    plt.show()
