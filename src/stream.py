
import ffmpeg
import subprocess as sp
import cv2
import numpy as np
import time
cap = cv2.VideoCapture(0)

# process = sp.Popen(ffmpeg_command, stdin=sp.PIPE)
_stream = (ffmpeg
    .input('pipe:', framerate='{}'.format(cap.get(cv2.CAP_PROP_FPS)), format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    .output('rtsp://0.0.0.0:8554/stream', format='rtsp', pix_fmt='yuv420p', rtsp_transport='udp', vcodec='h264_nvenc', preset="p1", zerolatency='1',delay="0", bf='0', **{"profile:v":"baseline"})
)
print("FFmpeg args: ", ffmpeg.get_args(_stream))
process = (
    _stream
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

while cap.isOpened():
    ret, img = cap.read()
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
    cv2.imshow("img", img)
    a = cv2.waitKey(20)
    if a == ord('q'): 
        process.terminate()
        exit()