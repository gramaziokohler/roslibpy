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

# Copy entrypoint
COPY ./ros_entrypoint.sh /
COPY ./integration-tests.launch /

EXPOSE 9090

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
