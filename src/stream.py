
GUI=False

import ffmpeg
import subprocess as sp
import cv2
import numpy as np
import time
import sys

if len(sys.argv) < 2: 
    print("no camera ID passed in")
    exit()
vidID = int(sys.argv[1])
cap = cv2.VideoCapture(vidID)

kTargetFPS=20
kIMG_WIDTH=320
kIMG_HEIGHT=240

# process = sp.Popen(ffmpeg_command, stdin=sp.PIPE)
#s='{}x{}'.format(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))) s='{}x{}'.format(kIMG_WIDTH, kIMG_HEIGHT)
_stream = (ffmpeg
    .input('pipe:', framerate=str(int(kTargetFPS)), format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(kIMG_WIDTH, kIMG_HEIGHT)) #, rc="cbr"
    .output('rtsp://0.0.0.0:8554/stream'+str(vidID), flags2="fast", format='rtsp', pix_fmt='yuv420p', rtsp_transport='udp', vcodec='h264_nvmpi', preset="ultrafast", rc="cbr", **{"b:v":"300K"}) #, bf='0', **{"profile:v":"baseline"}
) 
print("FFmpeg args: ", ffmpeg.get_args(_stream))
process = (
    _stream
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

def mainLoop():
    ret, img = cap.read()
    #resize 
    cuda_img_buf = cv2.cuda_GpuMat()
    cuda_img_buf.upload(img)
    retBuf = cv2.cuda.resize(cuda_img_buf, (kIMG_WIDTH, kIMG_HEIGHT), interpolation=cv2.INTER_LINEAR)

    img = retBuf.download()

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
        # time.sleep((1/kTargetFPS) - (0.1*(1/kTargetFPS))) 
        return
    cv2.imshow("img", img)
    a = cv2.waitKey(20)
    if a == ord('q'): 
        process.terminate()
        exit()


time_start=time.time()
while True:
    cur_time = time.time()
    mainLoop()
    delta_left = (time_start + 1/kTargetFPS) - cur_time

    if delta_left < 0:
        delta_left = 0

    time_start =  cur_time
    time.sleep(delta_left)
