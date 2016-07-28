# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 09:39:59 2015

@author: jiayi
"""
import cv2
import numpy as np
def convertRotTranslateToMatrix(rvec,tvec):
    rotMat,jacobian = cv2.Rodrigues(rvec)
    projMatrix = np.zeros((4,4),np.float)
    projMatrix[0:3,0:3] = rotMat
    projMatrix[0,3] = tvec[0][0]
    projMatrix[1,3] = tvec[1][0]
    projMatrix[2,3] = tvec[2][0]
    projMatrix[3,3] = 1.0
    return projMatrix
def getRotateTranslateMatrix(cameraModel,clickedPoints,cornerPoints):
    pointsNum = clickedPoints.shape[0]
    nz = -cameraModel.imagesize[1] / 8.0
    nx = cameraModel.imagesize[1] / 2.0
    ny = cameraModel.imagesize[0] / 2.0
    cameraMatrix = np.array([[nz,0,nx],[0,nz,ny],[0,0,1.0]])
    objectPoints = np.hstack((cornerPoints,np.zeros((pointsNum,1))))
    calibPoints = np.empty((pointsNum,2),np.float)
    for i in range(pointsNum):
        calibPoint = cameraModel.cam2world((clickedPoints[i,1],clickedPoints[i,0]))
        calibPoints[i] = [nz * calibPoint[1] / calibPoint[2] + nx,nz * calibPoint[0] / calibPoint[2] + ny]
    retVal,rvec,tvec = cv2.solvePnP(objectPoints,calibPoints,cameraMatrix,np.zeros(4))
    projMatrix = convertRotTranslateToMatrix(rvec,tvec)
    return projMatrix
def getPosByProjMat(projMatrix):
    cameraPos = np.dot(-np.linalg.inv(projMatrix[0:3,0:3]),projMatrix[0:3,3])
    return cameraPos
def saveProjMatrix(projMatrix,filename):
    f = open(filename,'w')
    for i in range(4):
        f.write('%f\t%f\t%f\t%f\n' % (projMatrix[i][0],projMatrix[i][1],projMatrix[i][2],projMatrix[i][3]))
    pos = getPosByProjMat(projMatrix)
    f.write('%f\t%f\t%f\n' % (pos[0],pos[1],pos[2]))
    f.close()