import launch
import launch_ros
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    
    # =============================================
    # 1. 获取功能包安装路径
    # =============================================
    urdf_tutorial_path = get_package_share_directory('fishbot_description')
    
    # =============================================
    # 2. 默认 URDF 文件路径
    # =============================================
    default_model_path = urdf_tutorial_path + '/urdf/first_robot.urdf'
    
    # =============================================
    # 3. 【代码清单 6-9】默认 RViz 配置文件路径
    #    需要在 config/rviz/ 目录下保存 display_model.rviz
    # =============================================
    default_rviz_config_path = urdf_tutorial_path + '/config/rviz/display_model.rviz'
    
    # =============================================
    # 4. 声明 model 参数（允许用户指定 URDF）
    # =============================================
    declare_model_arg = DeclareLaunchArgument(
        name='model',
        default_value=str(default_model_path),
        description='URDF 的绝对路径'
    )
    
    # =============================================
    # 5. 读取 URDF 内容（使用 cat 命令）
    # =============================================
    robot_description = launch_ros.parameter_descriptions.ParameterValue(
        Command(['xacro ', LaunchConfiguration('model')]),
        value_type=str
    )
    
    # =============================================
    # 6. robot_state_publisher 节点
    # =============================================
    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )
    
    # =============================================
    # 7. joint_state_publisher 节点
    # =============================================
    joint_state_publisher_node = launch_ros.actions.Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
    )
    
    # =============================================
    # 8. 【代码清单 6-9】RViz 节点（加载配置文件）
    #    arguments 和 parameters 的区别：
    #    - parameters：传递给节点的参数（键值对）
    #    - arguments：命令行参数（相当于在终端输入 rviz2 -d 配置文件）
    # =============================================
    rviz_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', default_rviz_config_path]   # -d 表示加载配置文件
    )
    
    # =============================================
    # 9. 返回 LaunchDescription
    # =============================================
    return launch.LaunchDescription([
        declare_model_arg,
        joint_state_publisher_node,
        robot_state_publisher_node,
        rviz_node
    ])