import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # 机器人模型名称（在 Gazebo 中显示的名称）
    robot_name_in_model = "fishbot"

    # 获取 fishbot_description 功能包的安装路径
    urdf_tutorial_path = get_package_share_directory('fishbot_description')

    # 默认 URDF/Xacro 模型文件路径
    default_model_path = urdf_tutorial_path + '/urdf/fishbot/fishbot.urdf.xacro'

    # 默认 Gazebo 世界文件路径。建图和导航使用干净房间，临时障碍物不写入该文件。
    default_world_path = urdf_tutorial_path + '/world/clean_room.world'

    # 声明 launch 参数（允许用户通过命令行指定模型文件）
    action_declare_arg_mode_path = launch.actions.DeclareLaunchArgument(
        name='model',
        default_value=str(default_model_path),
        description='URDF 的绝对路径'
    )

    # 是否启动 Gazebo GUI（无显示环境可设 false）
    action_declare_arg_gui = launch.actions.DeclareLaunchArgument(
        name='gui',
        default_value='true',
        description='Set to "false" to run headless'
    )

    action_declare_arg_world_path = launch.actions.DeclareLaunchArgument(
        name='world',
        default_value=str(default_world_path),
        description='Gazebo world 的绝对路径'
    )

    # 使用 xacro 命令将 Xacro 文件转换为 URDF 格式
    # 然后作为 robot_description 参数的值
    robot_description = launch_ros.parameter_descriptions.ParameterValue(
        launch.substitutions.Command(
            ['xacro ', launch.substitutions.LaunchConfiguration('model')]
        ),
        value_type=str
    )

    # robot_state_publisher 节点
    # 作用：发布 /robot_description 话题，供 Gazebo 使用
    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )

    # 通过 IncludeLaunchDescription 包含 gazebo_ros 的 launch 文件
    # 作用：启动 Gazebo 仿真器
    launch_gazebo = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [get_package_share_directory('gazebo_ros'), '/launch', '/gazebo.launch.py']
        ),
        # 传递参数给 Gazebo
        launch_arguments=[
            ('world', launch.substitutions.LaunchConfiguration('world')),   # 指定世界文件
            ('verbose', 'true'),             # 显示详细日志
            ('gui', launch.substitutions.LaunchConfiguration('gui'))
        ]
    )

    # spawn_entity 节点
    # 作用：从 /robot_description 话题获取 URDF，转换为 SDF，然后在 Gazebo 中生成机器人
    spawn_entity_node = launch_ros.actions.Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', '/robot_description',   # 订阅的话题
            '-entity', robot_name_in_model,    # 机器人在 Gazebo 中的名称
            '-x', '-0.5',
            '-y', '-5.5',
            '-z', '0.15'
        ]
    )

    # 返回 LaunchDescription（包含所有节点和动作）
    return launch.LaunchDescription([
        action_declare_arg_mode_path,
        action_declare_arg_gui,
        action_declare_arg_world_path,
        launch.actions.SetEnvironmentVariable(
            name='GAZEBO_MODEL_PATH',
            value=urdf_tutorial_path + '/world'
        ),
        robot_state_publisher_node,
        launch_gazebo,
        spawn_entity_node,
    ])
