
#############
# IMPORTANT #
#############
# THIS ASYNC MODULE MUST BE RAN WITH THE ENTERY POINT OF THE PROGRAM COVER UNDER if __name__ == '__main__': ...
# otherwise threading will fail


import cv2

import multiprocessing
import queue

#set multiprocessing to spawn new process instead of fork to avoid problems such as cuda no initializing correctly
multip_ctx = multiprocessing.get_context("spawn")
### HELPERS

class model_detections:
    def __init__(self, detections, thresholdPercentage=0.6) -> None:
        self.index = 0
        self.boxes = []
        self.scores = []

        num_detections = int(detections.pop('num_detections'))
        if num_detections <= 0: return

        detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
        for i in range(num_detections): 
            score = detections['detection_scores'][i]
            if score < thresholdPercentage: continue
            self.boxes.append(detections['detection_boxes'][i])
            self.scores.append(score)
            self.index += 1

def draw_boxes(detections: model_detections, img: cv2.Mat) -> cv2.Mat:
    height, width = img.shape[:2]
    for i in range(detections.index):
        ymin, xmin, ymax, xmax = detections.boxes[i]
        # tf gives us relative cordinates so we have to convert them to image cords
        ymin, xmin, ymax, xmax = (int(ymin * height), int(xmin * width), int(ymax * height), int(xmax * width))
        img = cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (2, 242, 122), 2)
        img = cv2.putText(img, str(round(detections.scores[i], 2)), (xmin, ymin), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 2)
    return img


### the detector

class Detector:
    def __init__(self, modelPath: str, thresholdPercentage=0.6):
        self.modelPath = modelPath
        self.kThresholdPercentage = thresholdPercentage

        self.detections: model_detections = model_detections({"num_detections": 0}) # place holder
        self.newFrame: cv2.Mat = False

        #queues for threading
        self.image_queue = multip_ctx.Queue(1)
        self.result_queue = multip_ctx.Queue(1)
        self.result_queue.put_nowait(model_detections({"num_detections": 0})) # put a placeholder in the queue so that update() will work correctly
        
        #threads
        self.__inference_thread = multip_ctx.Process(target=self._inference_thread, daemon=True)
        self.__inference_thread.start()

    def _inference_thread(self): # this is bascially a python script in it self
        print("Sub processed started")
        import tensorflow as tf 
        import object_detection

        # Enable GPU dynamic memory allocationS
        gpus = tf.config.experimental.list_physical_devices('GPU')
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

        self.model = tf.saved_model.load(self.modelPath)

        while True:
            frame = self.image_queue.get()
            input_tensor = tf.convert_to_tensor(frame)
            input_tensor = input_tensor[tf.newaxis, ...] # ssd expects a input tensor with shape of [1, Any, Any, 3]
            detections = self.model(input_tensor)
            detections_cleaned = model_detections(detections, self.kThresholdPercentage)
            try: self.result_queue.put_nowait(detections_cleaned)
            except: print("can't put new detection results into queue, skipping")

    # uploads new image if possible & return a detection
    def update(self, frame: cv2.Mat):
        if self.result_queue.full(): # there's a result in the queue
            try: # get it if there it is and tell the main thread
                self.detections = self.result_queue.get_nowait()

                if self.image_queue.empty(): # if image queue is empty, upload frame
                    try: 
                        self.image_queue.put_nowait(frame)
                    except(queue.Full):
                        print("Image Queue to processing thread is full while reporting avaliable")
                
            except(queue.Empty): 
                print("Failed to get result, queue reporting full while empty") 
        return self.detections # just return the old detections if one if not availiable or we failed to get it
    


