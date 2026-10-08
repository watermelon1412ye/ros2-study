import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 获取功能包路径
    pkg_path = get_package_share_directory('fishbot_description')
    
    # 模型文件路径
    urdf_path = os.path.join(pkg_path, 'urdf/fishbot/fishbot.urdf.xacro')
    
    # 世界文件路径（如果存在）
    world_path = os.path.join(pkg_path, 'world/custom_room.world')
    
    # 启动 Gazebo 并加载世界
    gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', world_path],
        output='screen'
    )
    
    # 使用 xacro 转换并生成 robot_description
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': ['xacro ', urdf_path]
        }]
    )
    
    # 生成机器人模型到 Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'fishbot', '-topic', 'robot_description'],
        output='screen'
    )
    
    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_robot
    ])