#! /bin/bash 

if [[ -z $1 ]]; then
    echo "Needs a export model name"
    exit 1
fi;

source /home/administrator/Desktop/vision/bash_init.bash 
export TF_GPU_ALLOCATOR=cuda_malloc_async #very important otherwise it runs out of memory
# MODEL_DIR="/home/administrator/Desktop/vision/ai2024/centernet_notedetection_512x512"
MODEL_DIR="/home/administrator/Desktop/vision/ai2024/mobilenet_notedetection_640x640"
python /home/administrator/Desktop/vision/ai2024/scripts/exporter_main_v2.py --input_type image_tensor --pipeline_config_path $MODEL_DIR/pipeline.config --trained_checkpoint_dir $MODEL_DIR --output_directory /home/administrator/Desktop/vision/ai2024/exported_models/$1