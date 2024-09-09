from skimage import io
from sklearn.cluster import MiniBatchKMeans,KMeans
#from numba import *
import numpy as np
import cv2
from colorfulness import image_colorfulness


class Compress():
    def __init__(self,image_path,output_path):
        self.image_path = image_path
        self.rows = []
        self.col = []
        self.output_path = output_path
        self.img_regularize()
        
    def img_regularize(self):
        self.img   = cv2.imread(self.image_path)
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        r ,g , b = cv2.split(self.img)
        #r_scaled ,g_scaled ,b_scaled = r/255, g/255, b/255
        #self.img = (cv2.merge((r_scaled,g_scaled,b_scaled)))
        # OP's original method
        B, G, R = cv2.split(self.img.astype("float"))
        score, *others   = image_colorfulness(self.img,B=B,G=G,R=R)
        self.img_reShape()

    def img_reShape(self):
        self.rows, self.cols = self.img.shape[0], self.img.shape[1]
        self.img = self.img.reshape(self.rows * self.cols, 3)
        self.img_train()
        

    def img_train(self):
        self.MPKM = MiniBatchKMeans(40,n_init=20)
        print("Compressing Image......")
        self.MPKM.fit(self.img)
        print("Image Compressed!")
        self.img_reconstruct()

    def img_reconstruct(self):

        self.centers = np.asarray(self.MPKM.cluster_centers_, dtype = np.uint8)
        self.labels = np.asarray(self.MPKM.labels_, dtype = np.uint8)
            
        self.labels = np.reshape(self.labels, (self.rows,self.cols))
        newImage = np.zeros((self.rows, self.cols, 3), dtype = np.uint8)
        for i in range(self.rows):
            for j in range(self.cols):
                # assinging every pixel the rgb color of their label's center 
                newImage[i, j, :] = self.centers[self.labels[i, j], :]
        
        io.imsave(self.output_path,newImage)
        return newImage