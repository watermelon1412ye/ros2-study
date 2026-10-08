import os

import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    autopatrol_robot_dir = get_package_share_directory('autopatrol_robot')
    patrol_config_path = os.path.join(
        autopatrol_robot_dir, 'config', 'patrol_config.yaml'
    )

    # The speaker provides /speech_text; patrol_node can still run if it falls
    # back to log-only speech, but launching both matches the book architecture.
    speaker_node = launch_ros.actions.Node(
        package='autopatrol_robot',
        executable='speaker',
        name='speaker',
        output='screen',
    )

    patrol_node = launch_ros.actions.Node(
        package='autopatrol_robot',
        executable='patrol_node',
        name='patrol_node',
        parameters=[patrol_config_path],
        output='screen',
    )

    return launch.LaunchDescription([
        speaker_node,
        patrol_node,
    ])
