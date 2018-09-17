#!/usr/bin/env bash

xhost +
sudo docker run --rm -ti --net=host \
    --env DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
    -v /home/astwin/workspace/pycharm_workspace/poc-opencv/python_scripts:/tmp/python:rw \
    poc-opencv:0.1.0 python3.5 /tmp/python/server_camera_ip.py
xhost -