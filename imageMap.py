# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 15:51:07 2015

@author: jiayi
"""
import numpy as np

def imageMap(lutTabel,srcImage):
    dstShape = (lutTabel.shape[0],lutTabel.shape[1],srcImage.shape[2])
    dstImage = np.zeros(dstShape,np.uint8)
    for i in np.arange(dstShape[0]):
        for j in np.arange(dstShape[1]):
            y,x = lutTabel[i,j,:]
            if y >= srcImage.shape[0] - 1 or y <= 0 or x >= srcImage.shape[1] - 1 or x <= 0:
                continue
            intx = int(x)
            inty = int(y)
            factorx = x - intx
            factory = y - inty
            dstImage[i,j,:] = factorx*factory*srcImage[inty+1,intx+1,:] + factorx*(1 - factory)*srcImage[inty,intx+1,:] + (1-factorx)*factory*srcImage[inty+1,intx,:] + (1-factorx)*(1 - factory)*srcImage[inty,intx,:]
    return dstImage
def imageMerge(srcImages,labelTable,weight):
    minWeight = 1.0
    dstImage = np.zeros(srcImages[0].shape,np.uint8)
    for i in np.arange(dstImage.shape[0]):
        for j in np.arange(dstImage.shape[1]):
            label = labelTable[i,j]
            if label < 0:
                continue
            if label < 4:
                dstImage[i,j,:] = srcImages[label][i,j,:]
                continue
            xlabel = label / 4
            ylabel = label % 4
            if weight[i,j] < minWeight:
                minWeight = weight[i,j]
            dstImage[i,j,:] = srcImages[xlabel][i,j,:] * (1-weight[i,j]) + srcImages[ylabel][i,j,:] * (weight[i,j])
    print minWeight
    return dstImage
def pixelCountSrc(lutTabel,srcShape):
    countLut = np.zeros(srcShape,np.float)
    for i in np.arange(lutTabel.shape[0]):
        for j in np.arange(lutTabel.shape[1]):
            y,x = lutTabel[i,j,:]
            if abs(x) < 0.0001 or abs(y) < 0.0001:
                continue
            if y >= srcShape[0] - 1 or y <= 0 or x >= srcShape[1] - 1 or x <= 0:
                continue
            intx = int(x)
            inty = int(y)
            factorx = x - intx
            factory = y - inty
            countLut[inty+1,intx+1] += factorx*factory
            countLut[inty+1,intx] += (1-factorx)*factory
            countLut[inty,intx+1] += factorx*(1 - factory)
            countLut[inty,intx] += (1-factorx)*(1 - factory)
    return countLut
def getPixelCount(pixelCount,x,y):
    pixelCnt = 0.0
    intx = int(x)
    inty = int(y)
    factorx = x - intx
    factory = y - inty
    if intx < 0 or intx + 1 > pixelCount.shape[0] - 1 or inty < 0 or inty + 1 > pixelCount.shape[1] - 1:
        return 0.0
    pixelCnt += factorx*factory*pixelCount[intx+1,inty+1]
    pixelCnt += (1-factorx)*factory*pixelCount[intx,inty+1]
    pixelCnt += factorx*(1 - factory)*pixelCount[intx+1,inty]
    pixelCnt += (1-factorx)*(1 - factory)*pixelCount[intx,inty]
    return pixelCnt
def pixelCountDst(lutTabels,pixelCount,weight,labelTable):
    dstCntLut = np.zeros(labelTable.shape,np.float)
    for i in np.arange(dstCntLut.shape[0]):
        for j in np.arange(dstCntLut.shape[1]):
            curLable = labelTable[i,j]
            if curLable < 0:
                continue
            if curLable < 4:
                x,y = lutTabels[curLable][i,j]
                dstCntLut[i,j] = getPixelCount(pixelCount[curLable],x,y)
                continue
            xlable = curLable / 4
            ylable = curLable % 4
            x,y = lutTabels[xlable][i,j]
            xDstCntLut = getPixelCount(pixelCount[xlable],x,y)
            x,y = lutTabels[ylable][i,j]
            yDstCntLut = getPixelCount(pixelCount[ylable],x,y)
            dstCntLut[i,j] = xDstCntLut * (1-weight[i,j]) + yDstCntLut * (weight[i,j])
    return dstCntLut
def plotCountOnImage(cntLut,image):
    for i in range(cntLut.shape[0]):
        for j in range(cntLut.shape[1]):
            count = cntLut[i,j]
            if count > 0 and count < 1:
                image[i,j,0] = min(255,image[i,j,0] + 125)
            if count >=1 and count < 2:
                image[i,j,1] = min(255,image[i,j,1] + 125)
            if count >= 2 and count < 3:
                image[i,j,2] = min(255,image[i,j,2] + 125)
            if count >= 3 and count < 4:
                image[i,j,0] = min(255,image[i,j,0] + 125)
                image[i,j,1] = min(255,image[i,j,1] + 125)
            if count >= 4 and count < 5:
                image[i,j,0] = min(255,image[i,j,0] + 125)
                image[i,j,2] = min(255,image[i,j,2] + 125)
            if count >= 5 and count < 6:
                image[i,j,1] = min(255,image[i,j,1] + 125)
                image[i,j,2] = min(255,image[i,j,2] + 125)
            if count >= 6:
                image[i,j,0] = min(255,image[i,j,0] + 125)
                image[i,j,1] = min(255,image[i,j,1] + 125)
                image[i,j,2] = min(255,image[i,j,2] + 125) 
        
            
            