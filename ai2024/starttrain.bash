
#! /bin/bash 

source /home/administrator/Desktop/vision/bash_init.bash 
export TF_GPU_ALLOCATOR=cuda_malloc_async #very important otherwise it runs out of memory
# MODEL_DIR="/home/administrator/Desktop/vision/ai2024/centernet_notedetection_512x512"
MODEL_DIR="/home/administrator/Desktop/vision/ai2024/mobilenet_notedetection_640x640"
python3 /home/administrator/Desktop/vision/ai2024/scripts/model_main_tf2.py --model_dir=$MODEL_DIR --pipeline_config_path=$MODEL_DIR/pipeline.config 2>&1 | tee -a test.log
