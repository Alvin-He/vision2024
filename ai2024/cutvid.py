import cv2

writeDirectory = "/home/administrator/Desktop/vision/ai2024/annotations/img_rec"
vid = cv2.VideoCapture("/home/administrator/Desktop/vision/ai2024/WIN_20240205_16_22_51_Pro.mp4")

seqTime = 0.5 # seconds, wait time per snapshot

amount_of_Frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
fps = vid.get(cv2.CAP_PROP_FPS)

frames_per_step = int(fps * seqTime)
num_steps = int(amount_of_Frames / frames_per_step)

for i in range(1, amount_of_Frames, frames_per_step):
    vid.set(cv2.CAP_PROP_POS_FRAMES, i-1)
    ret,frame = vid.read()
    if not ret: print("Skipped Frame {}".format(str(i)))
    cv2.imwrite("{}/{}.jpg".format(writeDirectory, str(i)), frame)
