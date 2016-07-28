# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 16:00:19 2015

@author: jiayi
"""
import numpy as np
from PIL import Image
import matplotlib.pylab as plt
import cv2
class StitchParam(object):
    def __init__(self):
        self.frontRearLen = 0
        self.chessHeight = 0
        self.chessInnerWidth = 0
        self.chessOuterWidth = 0
    def getFrontCalibPoints(self):
        calibPoints = np.empty((8,2),np.float)
        calibPoints[0] = [-self.chessInnerWidth, self.frontRearLen / 2 + self.chessHeight]
        calibPoints[1] = [0, self.frontRearLen / 2 + self.chessHeight]
        calibPoints[2] = [self.chessInnerWidth, self.frontRearLen / 2 + self.chessHeight]
        calibPoints[3] = [-(self.chessOuterWidth + self.chessInnerWidth), self.frontRearLen / 2]
        calibPoints[4] = [-self.chessInnerWidth, self.frontRearLen / 2]
        calibPoints[5] = [0, (self.frontRearLen / 2)]
        calibPoints[6] = [self.chessInnerWidth, (self.frontRearLen / 2)]
        calibPoints[7] = [(self.chessOuterWidth + self.chessInnerWidth), (self.frontRearLen / 2)]
        return calibPoints
    def getRearCalibPoints(self):
        calibPoints = np.empty((8,2),np.float)
        calibPoints[0] = [-self.chessInnerWidth, self.frontRearLen / 2 + self.chessHeight]
        calibPoints[1] = [0, -(self.frontRearLen / 2 + self.chessHeight)]
        calibPoints[2] = [-self.chessInnerWidth, -(self.frontRearLen / 2 + self.chessHeight)]
        calibPoints[3] = [(self.chessInnerWidth + self.chessOuterWidth), -(self.frontRearLen / 2)]
        calibPoints[4] = [self.chessInnerWidth, -(self.frontRearLen / 2)]
        calibPoints[5] = [0, -(self.frontRearLen / 2)]
        calibPoints[6] = [-self.chessInnerWidth, -(self.frontRearLen / 2)]
        calibPoints[7] = [-(self.chessInnerWidth + self.chessOuterWidth), -(self.frontRearLen / 2)]
        return calibPoints
    def getLeftCalibPoints(self):
        calibPoints = np.empty((6,2),np.float)
        calibPoints[0] = [-(self.chessInnerWidth + self.chessOuterWidth), -(self.frontRearLen / 2)]
        calibPoints[1] = [-(self.chessInnerWidth + self.chessOuterWidth), 0]
        calibPoints[2] = [-(self.chessInnerWidth + self.chessOuterWidth), (self.frontRearLen / 2)]
        calibPoints[3] = [-self.chessInnerWidth, -(self.frontRearLen / 2)]
        calibPoints[4] = [-self.chessInnerWidth, 0]
        calibPoints[5] = [-self.chessInnerWidth, (self.frontRearLen / 2)]
        return calibPoints
    def getRightCalibPoints(self):
        calibPoints = np.empty((6,2),np.float)
        calibPoints[0] = [(self.chessInnerWidth + self.chessOuterWidth), (self.frontRearLen / 2)]
        calibPoints[1] = [(self.chessInnerWidth + self.chessOuterWidth), 0]
        calibPoints[2] = [(self.chessInnerWidth + self.chessOuterWidth), -(self.frontRearLen / 2)]
        calibPoints[3] = [self.chessInnerWidth, (self.frontRearLen / 2)]
        calibPoints[4] = [self.chessInnerWidth, 0]
        calibPoints[5] = [self.chessInnerWidth, -(self.frontRearLen / 2)]
        return calibPoints
    def getCalibPoints(self,direction):
        calibPointFuns = [self.getFrontCalibPoints,self.getRearCalibPoints,self.getLeftCalibPoints,self.getRightCalibPoints]
        return calibPointFuns[direction]()
    def __str__(self):
        s = ' frontRearLen:' + str(self.frontRearLen) + \
        '\n chessHeight:' + str(self.chessHeight) + \
        '\n chessInnerWidth:' + str(self.chessInnerWidth) + \
        '\n chessOuterWidth:' + str(self.chessOuterWidth)
        return s
def getCornerPoints(frontRearLen,chessHeight,chessInnerWidth,chessOuterWidth,direction):
    stitchParam = StitchParam();
    stitchParam.chessHeight = chessHeight
    stitchParam.frontRearLen = frontRearLen
    stitchParam.chessInnerWidth = chessInnerWidth
    stitchParam.chessOuterWidth = chessOuterWidth
    cornerPoints = stitchParam.getCalibPoints(direction)
    return cornerPoints
def getStitchParamByFile(filename):
    f = open(filename)
    stitchParam = StitchParam();
    data = []
    i = 0
    while True:
        s = f.readline().strip()
        if s != '':
            i = i + 1
            data.append(float(s.split()[1]))
            if i == 4:
                break
    stitchParam.chessHeight = data[0]
    stitchParam.frontRearLen = data[1]
    stitchParam.chessInnerWidth = data[2]
    stitchParam.chessOuterWidth = data[3]
    return stitchParam
def getClickedPointsByFile(filename):
    f = open(filename)
    points = []
    line = f.readline().strip() 
    while line != '':
       points.append([float(ele) for ele in line.split()])
       line = f.readline().strip()
    return np.array(points,np.float)
def getClickedPointsByImage(filename,nPoints):
    im = np.array(Image.open(filename))
    plt.imshow(im)
    print 'Please click ' + str(nPoints) + 'points'
    x = plt.ginput(nPoints,-1)
    plt.show()
    return x
def getClickedPointByCornerDetect(filename,patternSize):
    img = cv2.imread(filename)
    retVal,corners = cv2.findChessboardCorners(img,(4,6))
    srcCorners = np.empty((corners.shape[0],2),np.float)
    for i in np.arange(corners.shape[0]):
        srcCorners[i] = corners[i][0]
    return srcCorners
def getDstCorner(offset,gridSize,patternSize,direction):
    dstCorners = np.empty((patternSize[0] * patternSize[1],2),np.float)
    for i in np.arange(patternSize[1]):
       for j in np.arange(patternSize[0]):
           if direction == 0:
               dstCorners[i * patternSize[0] + j] = (offset[0] + i * gridSize[0],offset[1] + j * gridSize[1]) 
           elif direction == 1:
               dstCorners[i * patternSize[0] + j] = (offset[0] - i * gridSize[0],offset[1] - j * gridSize[1]) 
           elif direction == 2:
               dstCorners[i * patternSize[0] + j] = (offset[0] - j * gridSize[1],offset[1] + i * gridSize[0])  
           elif direction == 3:
               dstCorners[i * patternSize[0] + j] = (offset[0] + j * gridSize[1],offset[1] - i * gridSize[0])
    return dstCorners
if __name__ == '__main__':
    print getCornerPoints(696.00,150.00,150.0,240.0,0)
    
    
        
        
        