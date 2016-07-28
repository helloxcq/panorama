# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 21:55:44 2015
高层函数，生成2D和3D全景
@author: jiayi
"""
import numpy as np
import ocamModel
import math
import py3DPanorama
import matplotlib.pylab as plt
import imageMap
import cv2
class PointMap(object):
    """
    已知内参和外参计算任意世界坐标系中任意一点在原始图像中的对应坐标
    """
    def __init__(self,ocam,projmat):
        self.ocam = ocam
        self.projmat = projmat
        self.campos = -np.dot(np.linalg.inv(projmat[:3,:3]),projmat[:3,3]) 
    def getMapPoint(self,point3D):
        point = np.array([point3D[1],point3D[0],point3D[2],1.0],np.float)
        calibPoint = np.dot(self.projmat,point)
        calibCoord = (-calibPoint[1],-calibPoint[0],-calibPoint[2])
        srcCoord = self.ocam.world2cam(calibCoord)
        return srcCoord  
def loadprojmat(filename):
    """
    导入前后左右四个方向的外参矩阵
    """
    f = open(filename)
    mat = []
    for i in range(4):
        line = [float(string) for string in f.readline().strip().split()]
        mat.append(line)
    projmat = np.array(mat,np.float)
    return projmat
def getRealPoint(point,mmPerPixel,innerRadius,outerRadius):
    """
    根据3D模型计算全景图像中的坐标对应的三维空间点
    """
    curlamda = 2.5
    maxheight = math.sqrt(outerRadius * outerRadius - innerRadius * innerRadius)
    point3D = [float(val) * mmPerPixel for val in point]
    if(point3D[2] <= innerRadius):
        return (point3D[0],point3D[1],0)
    if point3D[2] >= outerRadius:
        return (point3D[0],point3D[1],maxheight) 
    return (point3D[0],point3D[1],(maxheight - math.sqrt(outerRadius * outerRadius - point3D[2] * point3D[2]))*curlamda)
def getRealPoint2D(point,mmPerPixel,innerRadius,outerRadius):
    """
    根据2D模型计算全景图像中的坐标对应的三维地面点
    """
    point3D = [float(val) * mmPerPixel for val in point]
    return (point3D[0],point3D[1],0)
def generateTable(pointmap,point2dToPoint3dFun,curLabel,distance,curCam,mmPerPixel):
    """
    根据2D或者3D模型计算最终的查找表
    """
    lutshape = [curLabel.shape[0],curLabel.shape[1],2]
    lutTable = np.zeros(lutshape,np.float)
    for i in np.arange(curLabel.shape[0]):
        for j in np.arange(curLabel.shape[1]):
            label = curLabel[i,j]
            if label < 0:
                continue
            elif label == curCam:                 #当前区域为非融合区域
                point = point2dToPoint3dFun((-i + lutTable.shape[0] / 2,j - lutTable.shape[1] / 2,distance[i,j]),mmPerPixel,200,600)
                lutTable[i,j,:] = pointmap.getMapPoint(point)
                continue
            if label >= 4:                        #当前区域为融合区域
                xlabel = label / 4                #xlabel为2或者3，表示左侧区域或者右侧区域       
                ylabel = label % 4                #ylabel为0或者1，表示前侧区域或者后侧区域
                if xlabel == curCam or ylabel == curCam:
                    point = point2dToPoint3dFun((-i + lutTable.shape[0] / 2,j - lutTable.shape[1] / 2,distance[i,j]),mmPerPixel,200,600)
                    lutTable[i,j,:] = pointmap.getMapPoint(point)
    return lutTable
def CntTimes(cntLabel):
    maxCnt = int(np.max(cntLabel.reshape(-1)))+2
    cntTimes = np.zeros(maxCnt,np.int)
    print cntTimes.shape
    shape = cntLabel.shape
    for i in np.arange(shape[0]):
        for j in np.arange(shape[1]):
            cnt = cntLabel[i,j]
            if cnt == 0:
                continue
            cntTimes[round(cnt)] += 1            
    return cntTimes
def calCarRect(imageSize,realCarSize,mmPerPixel):
    carWidth = int(realCarSize[1] / mmPerPixel + 0.5)
    carHeight = int(realCarSize[0] / mmPerPixel + 0.5)
    carX = int((imageSize[1] - carWidth) / 2 + 0.5)
    carY = int((imageSize[0] - carHeight) / 2 + 0.5)
    return [carY,carY + carHeight - 1,carX,carX + carWidth - 1]
if __name__ == '__main__':
    mmPerPixel = 2.6
    direction = ['front','rear','left','right']
    point2dToPoint3dFun = getRealPoint;
    resultDir = 'test-3d/';
    srcShape = (576,720)
    dstShape = (480,360)
    carRect = calCarRect(dstShape,(510,170),2.6)
    print carRect
    minMergeAngle = math.pi * 3 / 16           #起始融合角
    maxMergeAngle = math.pi * 5 / 16           #结束融合角
    label,weight,distance=py3DPanorama.getPointInfoImage((480,360),carRect,minMergeAngle,maxMergeAngle)
                                               #label为目标图中每点在原图中的对应区域，weight为每点的融合权重，
                                               #distance为每点距离小车的距离
    srcCntLuts = []                            #原始图像的像素利用率
    lutTables = []                             #四路目标图像的查找表
    srcImages = []                             #四路原始图像
    dstImages = []                             #四路目标图像
    y,x = np.ogrid[0:576,0:720]
    for i in range(4):
        projmat = loadprojmat('param/'+direction[i] + '_transform.txt')
        print projmat
        ocam = ocamModel.OcamModel()
        ocam.getOcamModel('param/' + direction[i] + '_calib_results.txt',srcShape)
        pointmap = PointMap(ocam,projmat)
        lutTable = generateTable(pointmap,point2dToPoint3dFun,label,distance,i,mmPerPixel)            #生成一路查找表
        lutTables.append(lutTable)                             
        srcCntLut = imageMap.pixelCountSrc(lutTable,srcShape)          #计算原始图像像素利用率
        srcCntLuts.append(srcCntLut)
    for i in range(4):
        srcImage = cv2.imread('image/'+direction[i]+'0.bmp')
        srcImages.append(srcImage)
        dstImage = imageMap.imageMap(lutTables[i],srcImage)
        cv2.imwrite(resultDir + direction[i] + '_dst.jpg',dstImage);
        imageMap.plotCountOnImage(srcCntLuts[i],srcImages[i])
        cv2.imwrite(resultDir + direction[i] + '_ImgPlot.jpg',srcImages[i])
        dstImages.append(dstImage)
    dstImageMerge = imageMap.imageMerge(dstImages,label,weight)
    dstCntLut = imageMap.pixelCountDst(lutTables,srcCntLuts,weight,label)
#   imageMap.plotCountOnImage(dstCntLut,dstImageMerge)
    carImage=cv2.imread('image/car.jpg')
    resizedCar = cv2.resize(carImage,(carRect[3] - carRect[2],carRect[1] - carRect[0]))
    dstImageMerge[carRect[0]:carRect[1],carRect[2]:carRect[3],:] = resizedCar
    print 'hello,world'
    cv2.imwrite(resultDir + 'dstImg1.jpg',dstImageMerge)  
                
                
            