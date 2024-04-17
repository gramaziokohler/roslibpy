from roslibpy import Header as ROS1Header
from roslibpy import Time

__all__ = [
    "Header",
]


class Header(ROS1Header):
    """Represents a message header of the ROS type std_msgs/Header."""

    def __init__(self, stamp=None, frame_id=None):
        super(Header, self).__init__(stamp=stamp, frame_id=frame_id)
        self.data["stamp"] = Time(stamp["secs"], stamp["nsecs"]) if stamp else None
        self.data["frame_id"] = frame_id
        del self.data["seq"]
