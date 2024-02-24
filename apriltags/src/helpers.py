import cv2
import math
import numpy as np

# https://stackoverflow.com/a/44659589 with GPU  cuda resize
def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    cuda_img_buf = cv2.cuda.GpuMat()
    cuda_img_buf.upload(image)
    cuda_img_buf = cv2.cuda.resize(cuda_img_buf, dim, interpolation = inter)
    resized = cuda_img_buf.download()

    # return the resized image
    return resized

# implenmentaion of Rodugriz Rotation matrix to Euler angles based on
# https://d3cw3dd2w32x2b.cloudfront.net/wp-content/uploads/2012/07/euler-angles1.pdf
# or /docs/euler-angles
def rodRotMatToEuler(m):
    x = np.arctan2(m[1][2], m[2][2], dtype=np.double)
    c_2 = np.sqrt(m[0][0]**2 + m[0][1]**2, dtype=np.double)
    y = np.arctan2(-m[0][2], c_2)
    s_1 = np.sin(x, dtype=np.double)
    c_1 = np.cos(x, dtype=np.double)
    z = np.arctan2(s_1*m[2][0] - c_1 * m[1][0], c_1*m[1][1] - s_1*m[2][1], dtype=np.double)
    return (x, y, z)
