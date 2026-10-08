import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    fishbot_navigation2_dir = get_package_share_directory('fishbot_navigation2')
    slam_toolbox_dir = get_package_share_directory('slam_toolbox')

    use_sim_time = launch.substitutions.LaunchConfiguration('use_sim_time')
    rviz_config_path = fishbot_navigation2_dir + '/config/rviz/slam.rviz'

    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        launch.actions.IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [slam_toolbox_dir, '/launch', '/online_async_launch.py']
            ),
            launch_arguments={
                'use_sim_time': use_sim_time,
            }.items(),
        ),
        launch_ros.actions.Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2_slam',
            arguments=['-d', rviz_config_path],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'
        ),
    ])
