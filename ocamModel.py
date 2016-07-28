# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 21:42:50 2015
鱼眼摄像头的内参类
@author: jiayi
"""
import math
import matplotlib.pylab as plt
import numpy as np
from PIL import Image
class OcamModel(object):
    def __init__(self):
        self.pol = None
        self.invpol = None
        self.center = None
        self.tiltmat = None
        self.imagesize = None
        self.widthrate = None
    def getOcamModel(self,filename,imagesize):
        f = open(filename)
        
        print f.readline().strip()
        f.readline()
        self.pol = tuple([float(str) for str in f.readline().strip().split()[1:]])
        f.readline()
        
        print f.readline().strip()
        f.readline()
        self.invpol = tuple([float(str) for str in f.readline().split()[1:]])
        f.readline()
        
        print f.readline().strip()
        f.readline()
        self.center = tuple([float(str) for str in f.readline().strip().split()])
        f.readline()
        
        print f.readline().strip()
        f.readline()
        self.tiltmat = tuple([float(str) for str in f.readline().strip().split()])
        f.readline()
        
        print f.readline().strip()
        f.readline()
        self.imagesize = tuple([int(str) for str in f.readline().strip().split()])
        f.readline()
        
        widthrate = (imagesize[0] / self.imagesize[0],imagesize[1] / self.imagesize[1])
        self.widthrate = widthrate[1]
        self.center = (self.center[0] * widthrate[0],self.center[1] * widthrate[1])
        self.imagesize = imagesize
        f.close()
    def __str__(self):
        s = 'pol is:' + str(self.pol) + \
        '\ninvpol is:' + str(self.invpol) + \
        '\ncenter is:' + str(self.center) + \
        '\n tiltmat is:' + str(self.tiltmat) + \
        '\nimagesize is:' + str(self.imagesize)
        return s
        
    def world2cam(self,point3D):
        norm = math.sqrt(point3D[0] ** 2 + point3D[1] ** 2)
        if norm == 0:
            return tuple(self.center)
        theta = math.atan(point3D[2] / norm)
        coff = [math.pow(theta,i) * self.invpol[i] for i in range(len(self.invpol))]
        rho = sum(coff)
        lamdy = self.widthrate
        lamdx = lamdy * self.imagesize[0] * 4.0 / (3 * self.imagesize[1])
        x = point3D[0]*rho*lamdx/norm
        y = point3D[1]*rho*lamdy/norm
        point2Dx = x*self.tiltmat[0]+y*self.tiltmat[1]+self.center[0]
        point2Dy = x*self.tiltmat[2]+y*1.0+self.center[1] 
        return (point2Dx,point2Dy)
    def cam2world(self,point2D):
        invdet = 1.0 / (self.tiltmat[0]-self.tiltmat[1]*self.tiltmat[2])
        lamdy = self.widthrate
        lamdx = lamdy * self.imagesize[0] * 4.0 / (3 * self.imagesize[1])
        x = (point2D[0] - self.center[0]) / lamdx
        y = (point2D[1] - self.center[1]) / lamdy
        xp = invdet*(x - y * self.tiltmat[1])
        yp = invdet*(-self.tiltmat[2] * x + self.tiltmat[0] * y)
        r =math.sqrt(xp*xp+yp*yp)
        coff = [math.pow(r,i)*self.pol[i] for i in range(len(self.pol))]
        zp = sum(coff)
        invnorm = 1 / (xp*xp+yp*yp+zp*zp)
        point3D=(invnorm*xp,invnorm*yp,invnorm*zp)
        return point3D
    def calib2src(self,point2D,sf):
        nyc = self.imagesize[0] / 2.0
        nxc = self.imagesize[1] / 2.0
        nz = -self.imagesize[1] / sf
        calib3D = ((point2D[0] - nyc),(point2D[1] - nxc),nz)
        src2D = self.world2cam(calib3D)
        if src2D[0] > self.imagesize[0] - 1 or src2D[1] > self.imagesize[1] - 1 or src2D[0] < 0 or src2D[0] < 0:
            return (0,0)
        else:
            return src2D
    def src2calib(self,point2D,sf):
        nxc = self.imagesize[0] / 2.0
        nyc = self.imagesize[1] / 2.0
        nz = -self.imagesize[1] / sf
        calib3D = self.cam2world(point2D)
        calib2Dy = nz * calib3D[0] / calib3D[2] + nxc
        calib2Dx = nz * calib3D[1] / calib3D[2] + nyc
        return (calib2Dy,calib2Dx)
    def imagecalib(self,image):
        calibimage = np.empty_like(image)
        indx = np.empty(image.shape[:2],dtype = np.float)
        indy = np.empty(image.shape[:2],dtype = np.float)
        for i in np.arange(image.shape[0]):
            for j in np.arange(image.shape[1]):
                x,y = self.calib2src((i,j),6.0)
                indx[i,j],indy[i,j] = x,y
                calibimage[i,j,:] = image[round(x),round(y),:]
        return calibimage,indx,indy
def calibImage(imageFile,calibFile):
    image = np.array(Image.open(imageFile))
    ocam = OcamModel()
    ocam.getOcamModel(calibFile,image.shape[:2])
    plt.subplot(121)
    plt.imshow(image)
    plt.subplot(122)
    calibimage,indx,indy = ocam.imagecalib(image)
    plt.imshow(calibimage)
    plt.show()
if __name__ == '__main__':
    image = np.array(Image.open('shenzhen/rear/rear6.bmp'))
    print image.shape
    ocam = OcamModel()
    ocam.getOcamModel('shenzhen/parameter_8_13_freescale/rear_calib_results.txt',image.shape[:2])
    print ocam
    plt.subplot(121)
    plt.imshow(image)
    plt.subplot(122)
    calibimage,indx,indy = ocam.imagecalib(image)
    plt.imshow(calibimage)
    plt.show()
    