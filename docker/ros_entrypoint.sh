#!/bin/bash
set -e

# Source ROS distro environment
source "/opt/ros/$ROS_DISTRO/setup.bash"

exec "$@"
