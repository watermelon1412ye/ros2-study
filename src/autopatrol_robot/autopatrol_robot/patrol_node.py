import math
import os
import time

import cv2
import rclpy
from autopatrol_interfaces.srv import SpeachText
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.time import Time
from sensor_msgs.msg import Image
from tf2_ros import Buffer, TransformListener


def yaw_to_quaternion(yaw):
    half_yaw = yaw * 0.5
    return {
        'x': 0.0,
        'y': 0.0,
        'z': math.sin(half_yaw),
        'w': math.cos(half_yaw),
    }


def quaternion_to_yaw(quaternion):
    siny_cosp = 2.0 * (
        quaternion.w * quaternion.z + quaternion.x * quaternion.y
    )
    cosy_cosp = 1.0 - 2.0 * (
        quaternion.y * quaternion.y + quaternion.z * quaternion.z
    )
    return math.atan2(siny_cosp, cosy_cosp)


class PatrolNode(BasicNavigator):
    def __init__(self, node_name='patrol_node'):
        super().__init__(node_name)

        # Do not force use_sim_time in code.  It belongs in the launch/YAML
        # configuration: simulation needs true, while a physical robot needs
        # false.  That keeps the same node usable in both environments.
        self.declare_parameter('initial_point', [-0.424, -5.680, 0.024])
        self.declare_parameter('reset_initial_pose_on_start', False)
        self.declare_parameter('clear_costmaps_on_start', True)
        self.declare_parameter(
            'target_points',
            [-0.424, -5.680, 0.024, -0.424, -5.680, 0.024],
        )
        self.declare_parameter('patrol_loops', 1)
        self.declare_parameter('navigation_timeout_sec', 60.0)
        self.declare_parameter('image_save_path', '/tmp/autopatrol_images')

        self.initial_point_ = self.get_parameter('initial_point').value
        self.reset_initial_pose_on_start_ = bool(
            self.get_parameter('reset_initial_pose_on_start').value
        )
        self.clear_costmaps_on_start_ = bool(
            self.get_parameter('clear_costmaps_on_start').value
        )
        self.target_points_ = self.get_parameter('target_points').value
        self.patrol_loops_ = int(self.get_parameter('patrol_loops').value)
        self.navigation_timeout_sec_ = float(
            self.get_parameter('navigation_timeout_sec').value
        )
        self.image_save_path_ = self.get_parameter('image_save_path').value

        # TF is used to name saved images with the robot's map-frame pose.
        # The main loop calls spin_once frequently so the buffer keeps filling.
        self.buffer_ = Buffer(node=self)
        self.listener_ = TransformListener(self.buffer_, self)

        # The camera callback only caches the newest frame.  The patrol logic
        # decides when to save, usually after the robot reaches a target point.
        self.bridge_ = CvBridge()
        self.latest_image_ = None
        self.subscription_image_ = self.create_subscription(
            Image, '/camera_sensor/image_raw', self.image_callback, 10
        )

        # Speech is a service so patrol_node does not depend on one speech
        # implementation.  speaker.py may use real TTS or log-only fallback.
        self.speach_client_ = self.create_client(SpeachText, 'speech_text')

    def get_pose_by_xyyaw(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.position.z = 0.0

        orientation = yaw_to_quaternion(float(yaw))
        pose.pose.orientation.x = orientation['x']
        pose.pose.orientation.y = orientation['y']
        pose.pose.orientation.z = orientation['z']
        pose.pose.orientation.w = orientation['w']
        return pose

    def init_robot_pose(self):
        self.initial_point_ = self.get_parameter('initial_point').value
        initial_pose = self.get_pose_by_xyyaw(
            self.initial_point_[0],
            self.initial_point_[1],
            self.initial_point_[2],
        )

        self.setInitialPose(initial_pose)
        self.get_logger().info(
            'Initial pose sent: '
            f'x={self.initial_point_[0]:.3f}, '
            f'y={self.initial_point_[1]:.3f}, '
            f'yaw={self.initial_point_[2]:.3f}'
        )
        self.waitUntilNav2Active()

    def get_target_points(self):
        points = []
        self.target_points_ = self.get_parameter('target_points').value

        if len(self.target_points_) % 3 != 0:
            self.get_logger().warn(
                'target_points length must be a multiple of 3; ignoring tail values.'
            )

        for index in range(len(self.target_points_) // 3):
            x = float(self.target_points_[index * 3])
            y = float(self.target_points_[index * 3 + 1])
            yaw = float(self.target_points_[index * 3 + 2])
            points.append((x, y, yaw))
            self.get_logger().info(
                f'Loaded target point {index}: x={x:.3f}, y={y:.3f}, yaw={yaw:.3f}'
            )
        return points

    def nav_to_pose(self, target_pose):
        if len(self.initial_point_) >= 2:
            initial_dx = target_pose.pose.position.x - float(self.initial_point_[0])
            initial_dy = target_pose.pose.position.y - float(self.initial_point_[1])
            if math.hypot(initial_dx, initial_dy) < 0.10:
                # A target equal to the configured initial pose is a fixed-point
                # inspection task.  No path planning is needed in this case.
                self.get_logger().info('Target is the initial patrol point; mark reached.')
                return True

        current_pose = self.get_current_pose(timeout_sec=2.0)
        if current_pose is not None:
            dx = target_pose.pose.position.x - current_pose.translation.x
            dy = target_pose.pose.position.y - current_pose.translation.y
            distance = math.hypot(dx, dy)
            if distance < 0.10:
                # When the patrol point is the current pose, treat it as
                # reached directly.  This keeps fixed-point inspection demos
                # from entering Nav2 recovery for a zero-length path.
                self.get_logger().info(
                    f'Target already reached, distance={distance:.3f} m.'
                )
                return True

        self.goToPose(target_pose)

        while not self.isTaskComplete():
            feedback = self.getFeedback()
            if feedback is None:
                continue

            eta = Duration.from_msg(
                feedback.estimated_time_remaining
            ).nanoseconds / 1e9
            self.get_logger().info(
                f'distance_remaining={feedback.distance_remaining:.3f} m, '
                f'estimated_time_remaining={eta:.1f} s, '
                f'recoveries={feedback.number_of_recoveries}'
            )

            navigation_time = Duration.from_msg(feedback.navigation_time)
            if navigation_time > Duration(seconds=self.navigation_timeout_sec_):
                self.get_logger().warn('Navigation timeout, canceling task.')
                self.cancelTask()
                break

        result = self.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info('Navigation result: SUCCEEDED')
            return True
        if result == TaskResult.CANCELED:
            self.get_logger().warn('Navigation result: CANCELED')
            return False
        if result == TaskResult.FAILED:
            self.get_logger().error('Navigation result: FAILED')
            return False

        self.get_logger().error(f'Navigation result: invalid status {result}')
        return False

    def get_current_pose(self, timeout_sec=5.0):
        deadline = time.monotonic() + timeout_sec
        last_error = None

        while rclpy.ok() and time.monotonic() < deadline:
            # spin_once lets the TF and camera subscriptions receive data while
            # this synchronous helper waits for a transform.
            rclpy.spin_once(self, timeout_sec=0.1)
            try:
                tf = self.buffer_.lookup_transform(
                    'map', 'base_footprint', Time(seconds=0.0)
                )
                transform = tf.transform
                yaw = quaternion_to_yaw(transform.rotation)
                self.get_logger().info(
                    'Current pose: '
                    f'x={transform.translation.x:.3f}, '
                    f'y={transform.translation.y:.3f}, '
                    f'yaw={yaw:.3f}'
                )
                return transform
            except Exception as exc:
                last_error = exc

        self.get_logger().warn(f'Cannot get current pose: {last_error}')
        return None

    def image_callback(self, msg):
        self.latest_image_ = msg

    def record_image(self):
        deadline = time.monotonic() + 5.0
        while self.latest_image_ is None and rclpy.ok() and time.monotonic() < deadline:
            # Give the camera subscription a short window to receive its first
            # frame before deciding that image recording is unavailable.
            rclpy.spin_once(self, timeout_sec=0.1)

        if self.latest_image_ is None:
            self.get_logger().warn('No camera image received yet; skip recording.')
            return False

        pose = self.get_current_pose()
        if pose is None:
            self.get_logger().warn('No valid pose for image filename; skip recording.')
            return False

        os.makedirs(self.image_save_path_, exist_ok=True)
        filename = os.path.join(
            self.image_save_path_,
            f'image_{pose.translation.x:.2f}_{pose.translation.y:.2f}_'
            f'{int(time.monotonic() * 1000)}.png',
        )

        # cv_bridge converts ROS Image messages into OpenCV matrices before
        # cv2.imwrite stores them as normal image files.
        try:
            cv_image = self.bridge_.imgmsg_to_cv2(
                self.latest_image_, desired_encoding='bgr8'
            )
        except Exception as exc:
            self.get_logger().error(f'Cannot convert camera image: {exc}')
            return False

        if not cv2.imwrite(filename, cv_image):
            self.get_logger().error(f'Cannot write image: {filename}')
            return False

        self.get_logger().info(f'Image saved: {filename}')
        return True

    def speach_text(self, text):
        if not self.speach_client_.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn(f'Speech service unavailable, log only: {text}')
            return False

        request = SpeachText.Request()
        request.text = text
        future = self.speach_client_.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)

        if future.result() is None:
            self.get_logger().warn(f'Speech service request failed: {text}')
            return False

        if future.result().result:
            self.get_logger().info(f'Speech completed: {text}')
            return True

        self.get_logger().warn(f'Speech service returned failure: {text}')
        return False


def main(args=None):
    rclpy.init(args=args)
    patrol = PatrolNode()

    try:
        if patrol.reset_initial_pose_on_start_:
            patrol.speach_text('正在初始化位置')
            patrol.init_robot_pose()
            patrol.speach_text('位置初始化完成')
        else:
            patrol.get_logger().info(
                'Preserving the current AMCL pose; waiting for Nav2 to become active.'
            )
            patrol.waitUntilNav2Active()
            patrol.speach_text('导航系统已就绪')

        if patrol.clear_costmaps_on_start_:
            patrol.clearAllCostmaps()
            patrol.get_logger().info('Local and global costmaps cleared.')

        loop_index = 0
        while rclpy.ok():
            loop_index += 1
            patrol.get_logger().info(f'Start patrol loop {loop_index}.')

            for point_index, (x, y, yaw) in enumerate(patrol.get_target_points()):
                target_pose = patrol.get_pose_by_xyyaw(x, y, yaw)
                patrol.speach_text(f'准备前往目标点 {point_index}')

                if patrol.nav_to_pose(target_pose):
                    patrol.speach_text(f'已到达目标点 {point_index}，准备记录图像')
                    patrol.record_image()
                    patrol.speach_text('图像记录完成')
                else:
                    patrol.speach_text(f'目标点 {point_index} 导航失败')

            if patrol.patrol_loops_ > 0 and loop_index >= patrol.patrol_loops_:
                patrol.get_logger().info('Configured patrol loops finished.')
                break
    except (KeyboardInterrupt, ExternalShutdownException):
        patrol.get_logger().warn('Patrol interrupted, canceling current task.')
        try:
            patrol.cancelTask()
        except Exception as exc:
            patrol.get_logger().warn(f'Cancel task skipped: {exc}')
    finally:
        patrol.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
