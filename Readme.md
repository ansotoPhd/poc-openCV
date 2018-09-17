# Poc: dockerized openCV environment


--env DISPLAY=$DISPLAY sends the display id from the host to the container.

--env="QT_X11_NO_MITSHM=1" is required by OpenCV to show the display.

-v /dev/video0:/dev/video0 This lets the container find the camera.

-v /tmp/.X11-unix:/tmp/.X11-unix:ro This lets the container find the display via X server.