import math

from geometry_msgs.msg import PoseStamped


def yaw_to_quaternion(yaw):
    """Convert a planar yaw angle to a ROS quaternion."""
    half_yaw = yaw * 0.5
    return {
        'x': 0.0,
        'y': 0.0,
        'z': math.sin(half_yaw),
        'w': math.cos(half_yaw),
    }


def quaternion_to_yaw(quaternion):
    """Extract the planar yaw angle from a ROS quaternion."""
    siny_cosp = 2.0 * (
        quaternion.w * quaternion.z + quaternion.x * quaternion.y
    )
    cosy_cosp = 1.0 - 2.0 * (
        quaternion.y * quaternion.y + quaternion.z * quaternion.z
    )
    return math.atan2(siny_cosp, cosy_cosp)


def make_pose_stamped(node, x, y, yaw=0.0, frame_id='map'):
    pose = PoseStamped()
    pose.header.frame_id = frame_id
    pose.header.stamp = node.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.position.z = 0.0

    orientation = yaw_to_quaternion(float(yaw))
    pose.pose.orientation.x = orientation['x']
    pose.pose.orientation.y = orientation['y']
    pose.pose.orientation.z = orientation['z']
    pose.pose.orientation.w = orientation['w']
    return pose
