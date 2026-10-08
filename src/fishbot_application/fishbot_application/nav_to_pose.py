import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.duration import Duration

from fishbot_application.utils import make_pose_stamped


def main():
    rclpy.init()

    navigator = BasicNavigator()
    navigator.declare_parameter('goal_x', 1.0)
    navigator.declare_parameter('goal_y', -4.0)
    navigator.declare_parameter('goal_yaw', 0.0)
    navigator.declare_parameter('timeout_sec', 180.0)

    goal_x = navigator.get_parameter('goal_x').value
    goal_y = navigator.get_parameter('goal_y').value
    goal_yaw = navigator.get_parameter('goal_yaw').value
    timeout_sec = navigator.get_parameter('timeout_sec').value

    navigator.waitUntilNav2Active()

    goal_pose = make_pose_stamped(navigator, goal_x, goal_y, goal_yaw)

    # goToPose sends a NavigateToPose action goal to /navigate_to_pose.
    navigator.goToPose(goal_pose)
    navigator.get_logger().info(
        f'Sent navigation goal: x={goal_x:.3f}, y={goal_y:.3f}, '
        f'yaw={goal_yaw:.3f} rad'
    )

    interrupted = False
    try:
        feedback_count = 0
        while not navigator.isTaskComplete():
            feedback = navigator.getFeedback()
            if feedback is None:
                continue

            feedback_count += 1
            if feedback_count % 5 == 0:
                eta = Duration.from_msg(
                    feedback.estimated_time_remaining
                ).nanoseconds / 1e9
                navigator.get_logger().info(
                    f'distance_remaining={feedback.distance_remaining:.3f} m, '
                    f'estimated_time_remaining={eta:.1f} s, '
                    f'recoveries={feedback.number_of_recoveries}'
                )

            navigation_time = Duration.from_msg(feedback.navigation_time)
            if navigation_time > Duration(seconds=float(timeout_sec)):
                navigator.get_logger().warn('Navigation timeout, canceling task.')
                navigator.cancelTask()
                break
    except KeyboardInterrupt:
        interrupted = True
        navigator.get_logger().warn('Navigation interrupted, canceling task.')
        navigator.cancelTask()

    if not interrupted:
        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            navigator.get_logger().info('Navigation result: SUCCEEDED')
        elif result == TaskResult.CANCELED:
            navigator.get_logger().warn('Navigation result: CANCELED')
        elif result == TaskResult.FAILED:
            navigator.get_logger().error('Navigation result: FAILED')
        else:
            navigator.get_logger().error(f'Navigation result: invalid status {result}')

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
