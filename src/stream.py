
GUI=False

import ffmpeg
import subprocess as sp
import cv2
import numpy as np
import time
cap = cv2.VideoCapture(0)

kTargetFPS=10
kIMG_WIDTH=640
kIMG_HEIGHT=480

# process = sp.Popen(ffmpeg_command, stdin=sp.PIPE)
_stream = (ffmpeg
    .input('pipe:', framerate=str(kTargetFPS), format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    .crop(0, 0, 640, 480)
    .output('rtsp://0.0.0.0:8554/stream', format='rtsp', pix_fmt='yuv420p', rtsp_transport='udp', vcodec='h264_nvmpi', preset="ultrafast") #, bf='0', **{"profile:v":"baseline"}
) 
print("FFmpeg args: ", ffmpeg.get_args(_stream))
process = (
    _stream
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

cuda_img_buf = cv2.cuda.GpuMat()
while cap.isOpened():
    ret, img = cap.read()

    #resize 
    cuda_img_buf.upload(img)
    cuda_img_buf = cv2.cuda.resize(cuda_img_buf, (640, 480))

    img = cuda_img_buf.download()

    t = 'time:' + str(time.time())
    cv2.putText(img,t,(0,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,0, 0),1)
    # ffmepg x264 encoding 
    process.stdin.write(
        img
        .astype(np.uint8)
        .tobytes()
    )
    process.stdin.flush()
    # insert compression 
    # send net work time
    if not GUI:
        time.sleep((1/kTargetFPS) - (0.1*(1/kTargetFPS))) 
        continue
    cv2.imshow("img", img)
    a = cv2.waitKey(20)
    if a == ord('q'): 
        process.terminate()
        exit()
