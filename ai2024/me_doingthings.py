# The base code of this file is based off c-bassx's chess model code, https://github.com/c-bassx/chess-tensorflow. Special thanks to him
# import tensorflow as tf
import numpy as np
import cv2
import pandas as pd
import pathlib
import os
import matplotlib.pyplot as plt
kStartingImgDim=(640, 480)
kImgsFolderPath = "/home/administrator/Desktop/vision/ai2024/testImg/"


def openImg(path) -> cv2.Mat:
    img = cv2.imread(path, cv2.IMREAD_COLOR)

    cuda_img_buf = cv2.cuda.GpuMat()
    cuda_img_buf.upload(img)
    cuda_img_buf = cv2.cuda.resize(cuda_img_buf, kStartingImgDim)

    return cuda_img_buf.download()

imgs_folder = os.listdir(kImgsFolderPath)

train_db = pd.read_csv("/home/administrator/Desktop/vision/ai2024/notes.csv")[["image", "label"]]
train_imgs=[]
train_labels=[]
label_map = [{'name':'Note', 'id':1}]
for i in range(len(train_db["label"])):
    img = train_db["image"][i]
    label = train_db["label"][i]
    for j in imgs_folder:
        escapedPath = "_".join(j.split()) 
        if not escapedPath in img: continue
        sourceImg = openImg(kImgsFolderPath + j)
        train_imgs.append(sourceImg)
        break
    if type(label) == str:
        train_labels.append(1)
    else:
        train_labels.append(0)

plt.figure()
plt.imshow(train_imgs[0])
plt.colorbar()
plt.grid(False)
plt.show()
