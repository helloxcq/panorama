# -*- coding: utf-8 -*-
"""
Created on Tue Aug 04 19:39:42 2015
根据棋盘格角点计算外参矩阵
@author: jiayi
"""
import numpy as np
import cv2
import ocamModel
import rigidTransform
def getClickedPointByCornerDetect(filename,patternSize):
    img = cv2.imread(filename)
    grayImg = cv2.cvtColor(img,cv2.cv.CV_BGR2GRAY)
    retVal,corners = cv2.findChessboardCorners(img,patternSize)
    cv2.cornerSubPix(grayImg, corners, (11,11), (-1,-1),(cv2.cv.CV_TERMCRIT_EPS,100,1.e-6))
    srcCorners = np.empty((corners.shape[0],2),np.float)
    for i in np.arange(corners.shape[0]):
        srcCorners[i] = corners[i][0]
        cv2.circle(img,(int(srcCorners[i][0] + 0.5),int(srcCorners[i][1] + 0.5)),2 + i / 2,(0,0,255))
    cv2.imshow('img',img)
    cv2.waitKey()
    cv2.destroyAllWindows()
    return srcCorners
def getDstCorner(offset,gridSize,patternSize,direction):
    dstCorners = np.empty((patternSize[0] * patternSize[1],2),np.float)
    for i in np.arange(patternSize[1]):
       for j in np.arange(patternSize[0]):
           if direction == 0:
               dstCorners[i * patternSize[0] + j] = (offset[0] + j * gridSize[0],offset[1] - i * gridSize[1]) 
           elif direction == 1:
               dstCorners[i * patternSize[0] + j] = (offset[0] - j * gridSize[0],offset[1] + i * gridSize[1]) 
           elif direction == 2:
               dstCorners[i * patternSize[0] + j] = (offset[0] + i * gridSize[1],offset[1] + j * gridSize[0])  
           elif direction == 3:
               dstCorners[i * patternSize[0] + j] = (offset[0] - i * gridSize[1],offset[1] - j * gridSize[0])
    return dstCorners        
if __name__ == '__main__':
    imagesize = [576,720]
    projMatrixFile = ['param/front_transform.txt','param/rear_transform.txt',
                     'param/left_transform.txt','param/right_transform.txt']
    ocamModelFile = ['param/front_calib_results.txt','param/rear_calib_results.txt',
                     'param/left_calib_results.txt','param/right_calib_results.txt']
    offset = [(-55.2,370.1),(45.6,-371),(-175.3,14),(175.8,134.9)]
    gridSize = [(20,20),(20,20),(20,20),(20,20)]
    patternSize = [(6,4),(6,4),(6,4),(6,4)]
    imageFile = ['image/front0.bmp','image/rear0.bmp','image/left0.bmp','image/right0.bmp']
    for i in range(4):
        srcPoints = getClickedPointByCornerDetect(imageFile[i],patternSize[i])
        dstPoints = getDstCorner(offset[i],gridSize[i],patternSize[i],i)
        print dstPoints
        ocam = ocamModel.OcamModel()
        ocam.getOcamModel(ocamModelFile[i],imagesize)
        projMatrix = rigidTransform.getRotateTranslateMatrix(ocam,srcPoints,dstPoints)
        rigidTransform.saveProjMatrix(projMatrix,projMatrixFile[i])
        
        
        
    