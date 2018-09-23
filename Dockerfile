FROM ubuntu:16.04

RUN apt-get update && \
    # · utils/common
    apt-get install -y wget unzip locales \
    # · developer tools
    build-essential cmake pkg-config \
    # · image file formats
    libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev \
    # · video processing
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libxvidcore-dev libx264-dev \
    # · toolkit for creating graphical user interfaces
    libgtk-3-dev \
    # · libraries that are used to optimize various functionalities
    libatlas-base-dev gfortran \
    # · python3.5
    libssl-dev libpq-dev libfontconfig1 libfontconfig1-dev \
    python3.5 python3.5-dev

# · pip3.5 through easy_install-3.5
ADD https://bootstrap.pypa.io/ez_setup.py /tmp/ez_setup.py
RUN python3.5 /tmp/ez_setup.py && rm /tmp/ez_setup.py && \
    easy_install-3.5 pip

# · Numpy
RUN pip3.5 install numpy

RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

# => Install OpenCV
ADD https://github.com/opencv/opencv/archive/3.4.3.zip /tmp/opencv-3.4.3.zip
ADD https://github.com/opencv/opencv_contrib/archive/3.4.3.zip /tmp/opencv_contrib-3.4.3.zip
RUN cd /tmp && unzip opencv-3.4.3.zip && unzip opencv_contrib-3.4.3.zip && \
    rm opencv-3.4.3.zip && rm opencv_contrib-3.4.3.zip

RUN mkdir /tmp/opencv-3.4.3/build && cd /tmp/opencv-3.4.3/build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
          -D CMAKE_INSTALL_PREFIX=/usr/local \
          -D INSTALL_PYTHON_EXAMPLES=ON \
          -D INSTALL_C_EXAMPLES=OFF \
          -D OPENCV_EXTRA_MODULES_PATH=/tmp/opencv_contrib-3.4.3/modules \
          -D PYTHON3_EXECUTABLE=/usr/bin/python3.5 \
          -D BUILD_EXAMPLES=ON .. | tee /tmp/opencv-cmake-out.log

RUN cd /tmp/opencv-3.4.3/build && make -j7 && make install && rm -rf /tmp/opencv-3.4.3/ && rm -rf /tmp/opencv_contrib-3.4.3

RUN pip3.5 install dlib face_recognition imutils

RUN pip3.5 install flask

RUN apt-get install -y libcanberra-gtk3-module
RUN pip3.5 install tornado traitlets