FROM ros:iron
LABEL maintainer "Gonzalo Casas <casas@arch.ethz.ch>"

SHELL ["/bin/bash","-c"]

# Install rosbridge
RUN apt-get update && apt-get install -y \
    ros-iron-rosbridge-suite \
    # ros-iron-tf2-web-republisher \
    # ros-iron-ros-tutorials \
    # ros-iron-actionlib-tutorials \
    --no-install-recommends \
    # Clear apt-cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Copy entrypoint
COPY ./integration-tests.launch /

EXPOSE 9090

CMD ["bash"]
