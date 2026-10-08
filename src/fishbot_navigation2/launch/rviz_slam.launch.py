import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    use_sim_time = launch.substitutions.LaunchConfiguration('use_sim_time')
    rviz_config_path = (
        get_package_share_directory('fishbot_navigation2')
        + '/config/rviz/slam.rviz'
    )

    rviz_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        rviz_node
    ])
