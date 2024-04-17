FROM ros:noetic
LABEL maintainer "Gonzalo Casas <casas@arch.ethz.ch>"

SHELL ["/bin/bash","-c"]

# Install rosbridge
RUN apt-get update && apt-get install -y \
    ros-noetic-rosbridge-suite \
    ros-noetic-tf2-web-republisher \
    ros-noetic-ros-tutorials \
    ros-noetic-actionlib-tutorials \
    --no-install-recommends \
    # Clear apt-cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Copy launch
COPY ./integration-tests.launch /

EXPOSE 9090

CMD ["bash"]
