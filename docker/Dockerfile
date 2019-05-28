FROM ros:kinetic
LABEL maintainer "Gonzalo Casas <casas@arch.ethz.ch>"

# Install rosbridge
RUN apt-get update && apt-get install -y \
    ros-kinetic-rosbridge-suite \
    ros-kinetic-tf2-web-republisher \
    ros-kinetic-ros-tutorials \
    --no-install-recommends \
    # Clear apt-cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Copy entrypoint
COPY ./ros_entrypoint.sh /
COPY ./integration-tests.launch /

EXPOSE 9090

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]
