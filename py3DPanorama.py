# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np
import cv2
import math
import matplotlib.pylab as plt
def getLineSegment(curValue,minValue,maxValue):       #小于最小值为-1，大于最大值为1，其他为0
    if curValue < minValue:
        return -1
    elif curValue < maxValue:
        return 0
    else:
        return 1
def getPointMapInfo(x,y,carRect,minMergeAngle,maxMergeAngle):  #将全景区域分为9个区域，小车区域
    weight = 0.0                                               #前后左右四个非融合区域，
    distance = 0.0                                             #前左，前右，后左，后右四个区域中的                                                                           
    cmp1 = getLineSegment(x,carRect[0],carRect[1])             #在某个角度内属于融合区域
    cmp2 = getLineSegment(y,carRect[2],carRect[3])             
    label = [8,0,12,2,-1,3,9,1,13]   
    direction = [x,x,y,y]
    curLabel = label[(cmp2 + 1) + (cmp1 + 1) * 3]
    if curLabel < 0:
        return curLabel,weight,distance
    if curLabel < 4:
        distance = abs(carRect[curLabel] - direction[curLabel]) * 1.0
        return curLabel,weight,distance
    xLabel = curLabel % 4
    yLabel = curLabel / 4
    xDistance = abs(carRect[xLabel] - direction[xLabel]) * 1.0
    yDistance = abs(carRect[yLabel] - direction[yLabel]) * 1.0
    distance = math.sqrt(xDistance ** 2 + yDistance ** 2)
    if yDistance <= 0.000001:
        angle = math.pi / 2
    else:
        angle = math.atan(xDistance * 1.0 / yDistance)
    if angle < minMergeAngle:
        return yLabel,weight,distance
    if angle > maxMergeAngle:
        return xLabel,weight,distance
    weight = (angle - minMergeAngle) / (maxMergeAngle - minMergeAngle)
    return curLabel,weight,distance
def plotLabelImage(label,shape):
    label = label.reshape(shape)
    palette = np.array([[255,0,0],[0,255,0],[0,255,0],[0,255,0],[0,255,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,255],[0,0,255],[0,0,0],[0,0,0],[0,0,255],[0,0,255]],dtype = 'uint8')
    image = palette[label]
    plt.imshow(image)
    plt.show()   
def getPointInfoImage(imagesize,carRect,minMergeAngle,maxMergeAngle):
    x,y = np.mgrid[0:imagesize[0],0:imagesize[1]]
    x = x.flatten()
    y = y.flatten()
    weight = np.empty(x.shape,dtype = 'float')
    distance = np.empty(x.shape,dtype = 'float')
    label = np.empty(x.shape,dtype = 'int32')
    minMergeAngle = math.pi * 3 / 16
    maxMergeAngle = math.pi * 5 / 16
    for i in np.arange(x.shape[0]):
        label[i],weight[i],distance[i] = getPointMapInfo(x[i],y[i],carRect,minMergeAngle,maxMergeAngle)
    label = label.reshape(tuple(imagesize))
    distance = distance.reshape(tuple(imagesize))
    weight = weight.reshape(tuple(imagesize))  
    return label,weight,distance    
if __name__ == '__main__':
    image = cv2.imread('aroundView.jpg')
    carRect = [120,360,140,220]
    minMergeAngle = math.pi * 3 / 16
    maxMergeAngle = math.pi * 5 / 16
    label,weight,distance=getPointInfoImage((480,360),carRect,minMergeAngle,maxMergeAngle)
    plt.contourf(np.arange(360),np.arange(480),distance,50)
    plt.savefig('distance.jpg')
    plt.show()
    
    
    






