import cv2
import object_detection
import numpy as np
import tensorflow as tf
import time
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.utils import config_util
from object_detection.builders import model_builder
import math
import os
import helpers
import threading

HSV_NOTE_LOWERBOUND = (0, 80, 150) # s 115, v 150
HSV_NOTE_UPPERBOUND = (13,255,255)

# cap = cv2.VideoCapture('/home/administrator/Desktop/vision/ai2024/cresendoGameAnimation.mp4')
cap = cv2.VideoCapture('/home/administrator/Desktop/vision/ai2024/WIN_20240205_16_22_51_Pro.mp4')
# cap = cv2.VideoCapture(2)

# Enable GPU dynamic memory allocationS
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

labels = label_map_util.create_category_index_from_labelmap("/home/administrator/Desktop/vision/ai2024/annotations/label_map.pbtxt", use_display_name=True)
model = tf.saved_model.load("/home/administrator/Desktop/vision/ai2024/exported_models/02102024_ssd_rgb_11k/saved_model")

# # Load pipeline config and build a detection model
# configs = config_util.get_configs_from_pipeline_file("/home/administrator/Desktop/vision/ai2024/mobilenet_notedetection_640x640/pipeline.config")
# model_config = configs['model']
# detection_model = model_builder.build(model_config=model_config, is_training=False)

# # Restore checkpoint
# ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
# ckpt.restore(os.path.join("/home/administrator/Desktop/vision/ai2024/mobilenet_notedetection_640x640/", 'ckpt-15')).expect_partial()

# @tf.function
# def detect_fn(image):
#     """Detect objects in image."""

#     image, shapes = detection_model.preprocess(image)
#     prediction_dict = detection_model.predict(image, shapes)
#     detections = detection_model.postprocess(prediction_dict, shapes)

#     return detections


# def findPossibleNotes()
def runInference(frame: cv2.Mat):
    # img_for_inference = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    input_tensor = tf.convert_to_tensor(frame)
    
    # input_tensor = tf.convert_to_tensor(np.expand_dims(np.array(frame), 0), dtype=tf.float32)
    # The model expects a batch of images, so add an axis with `tf.newaxis`. (i don't really know why)
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = model(input_tensor)
    # detections = detect_fn(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    # num_detections = int(detections.pop('num_detections'))
    # print("detected: ")
    # print(num_detections)
    # detections = {key: value[0, :num_detections].numpy()
    #                for key, value in detections.items()}
    # detections['num_detections'] = num_detections

    # # detection_classes should be ints.
    # detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    # image_with_detections = frame.copy()

    #viz_utils.visualize_boxes_and_labels_on_image_array(
    #       image_with_detections,
    #       detections['detection_boxes'],
    #       detections['detection_classes'],
    #       detections['detection_scores'],
    #       labels,
    #       use_normalized_coordinates=True,
    #       max_boxes_to_draw=200,
    #       min_score_thresh=.50,
    #       agnostic_mode=False)
    return model_detections(detections)

class model_detections:
    def __init__(self, detections, thresholdPercentage=0.6) -> None:
        self.index = 0
        self.boxes = []
        self.scores = []

        num_detections = int(detections.pop('num_detections'))

        detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
        for i in range(num_detections): 
            score = detections['detection_scores'][i]
            if score < thresholdPercentage: continue
            self.boxes.append(detections['detection_boxes'][i])
            self.scores.append(score)
            self.index += 1
    
def draw_boxes(detections: model_detections, img) -> cv2.Mat:
    height, width = img.shape[:2]
    for i in range(detections.index):
        ymin, xmin, ymax, xmax = detections.boxes[i]
        # tf gives us relative cordinates so we have to convert them to image cords
        ymin, xmin, ymax, xmax = (int(ymin * height), int(xmin * width), int(ymax * height), int(xmax * width))
        img = cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (2, 242, 122), 2)
        img = cv2.putText(img, str(round(detections.scores[i], 2)), (xmin, ymin), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 2)
    return img

def main_loop():
    frame_num = 0
    tot_frame_time = 0
    while cap.isOpened():
        ret, img = cap.read()
        if not ret: 
            print("Finished, avergage frame time {}".format(tot_frame_time/frame_num))
            exit()
        frame_num += 1
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv, HSV_NOTE_LOWERBOUND, HSV_NOTE_UPPERBOUND)
        masked = cv2.bitwise_and(img, img, mask=mask)
        start = time.time_ns()
        detections = runInference(masked)
        proced_image = draw_boxes(detections, img)
        end = time.time_ns()
        frame_time = (end - start) * 1/1000000
        print("frame {}, time: {}ms".format(frame_num, frame_time))
        tot_frame_time += frame_time

        # resize for displaying
        final = helpers.image_resize(proced_image, width=640)        

        cv2.imshow("test", final)
        cv2.waitKey(1)


time_start=time.time_ns()
while True:
    time_start = time.time_ns()
    main_loop()
    delta_left = (time_start + (1/30) * 1000 * 1000 * 1000) - time.time_ns()
    
    time.sleep(abs(delta_left * (1/(1000*1000*1000))))

# img = cv2.imread('/home/administrator/Desktop/vision/ai2024/annotations/dataset/8c47de30-Screenshot_from_2024-01-27_22-11-02.png', cv2.IMREAD_COLOR)
# runInference(img)