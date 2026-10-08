import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

from fishbot_application.utils import make_pose_stamped


DEFAULT_WAYPOINTS = [
    (1.453, -5.932, -1.162),
    (1.453, -5.932, -1.162),
    (1.453, -5.932, -1.162),
]


def main():
    rclpy.init()

    navigator = BasicNavigator()
    navigator.waitUntilNav2Active()

    goal_poses = [
        make_pose_stamped(navigator, x, y, yaw)
        for x, y, yaw in DEFAULT_WAYPOINTS
    ]

    # followWaypoints sends a FollowWaypoints action goal to /follow_waypoints.
    # The feedback contains current_waypoint, so it is useful for patrol tasks.
    navigator.followWaypoints(goal_poses)
    navigator.get_logger().info(f'Sent {len(goal_poses)} waypoint goals.')

    interrupted = False
    try:
        last_waypoint = None
        while not navigator.isTaskComplete():
            feedback = navigator.getFeedback()
            if feedback is None:
                continue

            if feedback.current_waypoint != last_waypoint:
                last_waypoint = feedback.current_waypoint
                navigator.get_logger().info(
                    f'Current waypoint index: {feedback.current_waypoint}'
                )
    except KeyboardInterrupt:
        interrupted = True
        navigator.get_logger().warn('Waypoint navigation interrupted, canceling task.')
        navigator.cancelTask()

    if not interrupted:
        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            navigator.get_logger().info('Waypoint navigation result: SUCCEEDED')
        elif result == TaskResult.CANCELED:
            navigator.get_logger().warn('Waypoint navigation result: CANCELED')
        elif result == TaskResult.FAILED:
            navigator.get_logger().error('Waypoint navigation result: FAILED')
        else:
            navigator.get_logger().error(
                f'Waypoint navigation result: invalid status {result}'
            )

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
