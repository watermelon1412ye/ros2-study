import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator

from fishbot_application.utils import make_pose_stamped


def main():
    rclpy.init()

    navigator = BasicNavigator()
    navigator.declare_parameter('x', -0.424)
    navigator.declare_parameter('y', -5.680)
    navigator.declare_parameter('yaw', 0.024)

    x = navigator.get_parameter('x').value
    y = navigator.get_parameter('y').value
    yaw = navigator.get_parameter('yaw').value

    initial_pose = make_pose_stamped(navigator, x, y, yaw)

    # setInitialPose publishes to /initialpose for AMCL, equivalent to RViz's
    # "2D Pose Estimate" tool or a ros2 topic pub command.
    navigator.setInitialPose(initial_pose)
    navigator.get_logger().info(
        f'Sent initial pose: x={x:.3f}, y={y:.3f}, yaw={yaw:.3f} rad'
    )

    # Waiting here confirms Nav2 lifecycle nodes are active before this command exits.
    navigator.waitUntilNav2Active()
    navigator.get_logger().info('Nav2 is active and AMCL initial pose was sent.')

    rclpy.shutdown()


if __name__ == '__main__':
    main()
