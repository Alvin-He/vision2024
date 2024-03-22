from PIL import Image
import cv2
import numpy as np
import tensorflow.compat.v1  as tf
import os
import io

with tf.gfile.GFile(os.path.join('/home/administrator/Desktop/vision/ai2024/annotations/train/', '8c47de30-Screenshot_from_2024-01-27_22-11-02.png'), 'rb') as fid:
    encoded_jpg = fid.read()
encoded_jpg_io = io.BytesIO(encoded_jpg)
image = Image.open(encoded_jpg_io)
width, height = image.size

cvImg = np.array(image)