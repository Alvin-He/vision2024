#! /usr/bin/python3

import subprocess
import os

source_dir = "/mnt/1ECC5E47CC5E18FB/Users/alh/Desktop/vision/opencv_python/cv2"
target_lib_dir = "/mnt/1ECC5E47CC5E18FB/Users/alh/Desktop/vision/.venv/lib/python3.10/site-packages/cv2"


for dir_path, dir_names, filenames in os.walk(source_dir):
    rel_dir = dir_path.split(source_dir)[1]
    for f in filenames:
        if not f.endswith(".pyi"): continue
        dst_dir = target_lib_dir + rel_dir
        # print(source_dir + rel_dir + '/' + f)
        subprocess.run("mkdir -p {dst_dir} && cp -n {src} {dst}".format(src=source_dir + rel_dir + '/' + f, dst_dir=dst_dir, dst=dst_dir+'/'+f), shell=True)