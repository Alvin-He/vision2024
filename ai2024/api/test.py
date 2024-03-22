import note_detector
import helpers

import cv2
import time

if __name__ == '__main__':
        
    HSV_NOTE_LOWERBOUND = (0, 80, 150) # s 115, v 150
    HSV_NOTE_UPPERBOUND = (13,255,255)

    # cap = cv2.VideoCapture('/home/administrator/Desktop/vision/ai2024/cresendoGameAnimation.mp4')
    # cap = cv2.VideoCapture('/home/administrator/Desktop/vision/ai2024/WIN_20240205_16_22_51_Pro.mp4')
    cap = cv2.VideoCapture(2)

    detector = note_detector.Detector("./models/02102024_ssd_rgb_11k/checkpoint")

    frame_num = 0
    tot_frame_time = 0
    def main_loop():
        global frame_num, tot_frame_time
        ret, img = cap.read()
        if not ret: 
            print("Finished, avergage frame time {}".format(tot_frame_time/frame_num))
            exit()
        frame_num += 1
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv, HSV_NOTE_LOWERBOUND, HSV_NOTE_UPPERBOUND)
        masked = cv2.bitwise_and(img, img, mask=mask)
        # start = time.time_ns()
        detections = detector.update(masked)
        proced_image = note_detector.draw_boxes(detections, img)
        # end = time.time_ns()
        # frame_time = (end - start) * 1/1000000
        # print("frame {}, time: {}ms".format(frame_num, frame_time))
        # tot_frame_time += frame_time

        # resize for displaying
        final = helpers.image_resize(proced_image, width=640)        

        cv2.imshow("test", final)
        cv2.waitKey(1)

    amount_of_Frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)

    seconds_per_frame = 1/fps
    ns_per_frame = seconds_per_frame * 1000 * 1000 * 1000

    time_start=time.time_ns()
    while True:
        time_start = time.time_ns()
        main_loop()
        delta_left = (time_start + ns_per_frame) - time.time_ns()
        if delta_left < 0: delta_left = 0
        time.sleep(delta_left * (1/(1000*1000*1000)))