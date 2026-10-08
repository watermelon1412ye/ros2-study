# ROS 2 学习进度与命令速查

更新时间：2026-09-17

这个文件记录各章当前进度，以及按小节整理的“学习时直接使用的命令集合”。目前覆盖第 7 章；后续学习第 8、9 章时，在本文件继续新增对应章节的命令速查。详细学习过程、命令解释、流程图和排错记录统一写在章节日志里：

```text
notes/ROS2_第7章_自主导航学习日志.md
```

学习日志写作规范：

```text
notes/ROS2_学习日志写作规范.md
```

## 第 7 章命令速查

使用方式：学习某一小节时，先执行“通用终端初始化”，再按对应小节从“构建 → 启动 → 验证”的顺序操作。每新开一个 ROS 2 终端都要初始化一次。

### 通用终端初始化

~~~bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
~~~

修改 launch、config、maps 或 Python 节点后，要重新构建相关包，并再次 source install/setup.bash。

### 7.2 建图流程与仿真环境优化

构建建图相关包：

~~~bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select fishbot_description fishbot_navigation2 --event-handlers console_direct+
source install/setup.bash
~~~

三个终端依次启动 Gazebo、SLAM 和键盘控制：

~~~bash
ros2 launch fishbot_description gazebo_sim.launch.py
~~~

~~~bash
ros2 launch fishbot_navigation2 mapping.launch.py
~~~

~~~bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
~~~

确认 RViz 中墙体闭合、没有明显重影后保存地图：

~~~bash
cd /home/fishros/chapt6/chapt6_ws/src/fishbot_navigation2/maps
source /opt/ros/humble/setup.bash
source /home/fishros/chapt6/chapt6_ws/install/setup.bash
ros2 run nav2_map_server map_saver_cli -f room
~~~

保存地图后重新安装 fishbot_navigation2 的地图资源：

~~~bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select fishbot_navigation2 --event-handlers console_direct+
source install/setup.bash
~~~

建图检查：

~~~bash
ros2 topic echo /scan --once --no-daemon
ros2 topic echo /odom --once --no-daemon
timeout 4 ros2 run tf2_ros tf2_echo odom base_footprint
ls -lh src/fishbot_navigation2/maps/room.yaml src/fishbot_navigation2/maps/room.pgm
~~~

### 7.3 Navigation 2 基础导航与动态避障

构建并检查 Nav2 安装资源：

~~~bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select fishbot_navigation2 fishbot_description --event-handlers console_direct+
source install/setup.bash
find install/fishbot_navigation2/share/fishbot_navigation2 -maxdepth 3 -type f -o -type l | sort
~~~

两个终端依次启动 Gazebo 与 Nav2（第二条会打开 RViz）：

~~~bash
ros2 launch fishbot_description gazebo_sim.launch.py
~~~

~~~bash
ros2 launch fishbot_navigation2 navigation2.launch.py
~~~

RViz 操作：Fixed Frame 设为 map → 使用 2D Pose Estimate 校准 → 使用 Nav2 Goal 发送目标点。

导航、定位与避障检查：

~~~bash
ros2 launch fishbot_navigation2 navigation2.launch.py --show-args
ros2 topic echo /map --once --no-daemon
ros2 topic echo /scan --once --no-daemon
ros2 topic echo /amcl_pose --once --no-daemon
ros2 topic echo /cmd_vel --once --no-daemon
timeout 4 ros2 run tf2_ros tf2_echo map base_footprint
~~~

### 7.4 导航应用开发

构建并确认四个应用节点：

~~~bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select fishbot_navigation2 fishbot_application --event-handlers console_direct+
source install/setup.bash
ros2 pkg executables fishbot_application
~~~

先按 7.3 启动 Gazebo 与 Nav2，再依次运行：

~~~bash
ros2 run fishbot_application init_robot_pose
ros2 run fishbot_application get_robot_pose
ros2 run fishbot_application nav_to_pose
ros2 run fishbot_application waypoint_follower
~~~

get_robot_pose 适合独占一个终端持续观察；nav_to_pose 和 waypoint_follower 不要同时运行。

常用参数、Action 与控制检查：

~~~bash
ros2 run fishbot_application init_robot_pose --ros-args -p x:=-0.424 -p y:=-5.680 -p yaw:=0.024
ros2 run fishbot_application nav_to_pose --ros-args -p goal_x:=1.0 -p goal_y:=-4.0 -p goal_yaw:=0.0
ros2 action list
ros2 action info /navigate_to_pose -t
ros2 action info /follow_waypoints -t
ros2 topic echo /cmd_vel --once --no-daemon
timeout 4 ros2 run tf2_ros tf2_echo map base_footprint
~~~

### 7.5 自动巡检机器人（当前学习）

目标：巡检节点设置初始位姿，依次前往 target_points，调用 speech_text 服务，并把 /camera_sensor/image_raw 保存为 PNG。

首次运行或修改 7.5 的节点、配置后，先构建并检查：

~~~bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select autopatrol_interfaces autopatrol_robot --event-handlers console_direct+
source install/setup.bash
ros2 pkg executables autopatrol_robot
ros2 interface show autopatrol_interfaces/srv/SpeachText
ros2 launch autopatrol_robot autopatrol.launch.py --show-args
~~~

完整巡检需要三个终端。每个终端先执行“通用终端初始化”，再分别运行：

终端 1，Gazebo（机器人、雷达、相机）：

~~~bash
ros2 launch fishbot_description gazebo_sim.launch.py
~~~

终端 2，Nav2（地图、AMCL、导航 Action）：

~~~bash
ros2 launch fishbot_navigation2 navigation2.launch.py
~~~

终端 3，语音服务与巡检节点：

~~~bash
ros2 launch autopatrol_robot autopatrol.launch.py
~~~

运行前或运行中，用新终端检查 7.5 的依赖链路：

~~~bash
ros2 node list
ros2 service list | rg speech_text
ros2 service type /speech_text
ros2 action info /navigate_to_pose -t
ros2 topic echo /amcl_pose --once --no-daemon
ros2 topic echo /camera_sensor/image_raw --once --no-daemon
timeout 4 ros2 run tf2_ros tf2_echo map base_footprint
ros2 topic echo /cmd_vel --once --no-daemon
~~~

单独验证语音服务：

~~~bash
ros2 service call /speech_text autopatrol_interfaces/srv/SpeachText "{text: '自动巡检语音服务测试'}"
~~~

确认是否已记录图像：

~~~bash
find /tmp/autopatrol_images -maxdepth 1 -type f -name '*.png' -printf '%f %s bytes\n' | sort
~~~

巡检点、初始位姿、循环次数和图片目录都在：

~~~text
src/autopatrol_robot/config/patrol_config.yaml
~~~

其中 target_points 每三个数是一组 x, y, yaw，使用的是 map 坐标系，不是 Gazebo world 坐标系。修改配置后：

~~~bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select autopatrol_robot --event-handlers console_direct+
source install/setup.bash
ros2 launch autopatrol_robot autopatrol.launch.py
~~~

快速排错：

~~~bash
# 巡检卡在等待导航：确认 Nav2 已 active
ros2 lifecycle get /amcl
ros2 lifecycle get /bt_navigator

# 没有图片：确认相机数据与保存目录
ros2 topic echo /camera_sensor/image_raw --once --no-daemon
find /tmp/autopatrol_images -maxdepth 1 -type f -name '*.png'

# 小车不动或导航失败：确认定位和速度输出
ros2 topic echo /amcl_pose --once --no-daemon
ros2 topic echo /cmd_vel --once --no-daemon
~~~

当前环境未安装 Python espeakng 时，speaker 会将语音文本打印到日志作为兜底；服务调用和巡检流程仍可正常验证。

#### 7.5 实验现象与成功判据

使用推荐命令启动：

~~~bash
ros2 launch autopatrol_robot autopatrol.launch.py
~~~

终端中应依次看到以下现象：

~~~text
Speech completed: 正在初始化位置
Initial pose sent: x=-0.424, y=-5.680, yaw=0.024
Nav2 is ready for use!
Speech completed: 位置初始化完成
Start patrol loop 1.
Loaded target point ...
Speech completed: 准备前往目标点 ...
Speech completed: 已到达目标点 ...，准备记录图像
Current pose: x=..., y=..., yaw=...
Image saved: /tmp/autopatrol_images/image_....png
Speech completed: 图像记录完成
Configured patrol loops finished.
~~~

在 Gazebo 和 RViz 中应观察到：

- AMCL 初始位置被设置，RViz 中机器人与地图位置基本对齐。
- 如果目标点不同于当前位置，机器人规划路径并移动，/cmd_vel 出现非零速度。
- 到达每个目标点后调用语音服务并保存一张相机图片。
- 完成 patrol_loops 指定的巡检轮数后，patrol_node 正常退出。

当前 patrol_config.yaml 配置了 3 个相同的定点巡检目标，它们都等于初始位姿。因此当前实验中机器人不明显移动是正常现象，主要验证的是：

~~~text
初始化定位 → 识别目标点已经到达 → 调用语音服务 → 获取当前位置
→ 接收相机图像 → 保存图片 → 完成巡检
~~~

当前现场验证结果：

~~~text
Nav2：已激活
语音服务：/speech_text 在线
相机：/camera_sensor/image_raw 有 1 个发布者
机器人位姿：约 x=-0.426, y=-5.681, yaw=0.026
巡检图片：已成功保存到 /tmp/autopatrol_images
~~~

注意两种启动方式的区别：

- ros2 launch autopatrol_robot autopatrol.launch.py：启动 speaker 和 patrol_node，并加载 patrol_config.yaml，当前会执行 3 个配置目标点。
- ros2 run autopatrol_robot patrol_node：只启动巡检节点，不自动加载 YAML，使用代码中的 2 个默认目标点。

#### 7.5 亲手实验：观察机器人真正移动

第一步：打开巡检配置。

~~~bash
nano /home/fishros/chapt6/chapt6_ws/src/autopatrol_robot/config/patrol_config.yaml
~~~

把 target_points 改成下面两个已经验证过的地图坐标。第一个点让机器人驶向房间另一位置，第二个点让机器人返回起点：

~~~yaml
target_points: [
  1.498, -5.898, 1.692,
  -0.424, -5.680, 0.024
]
~~~

第二步：保存配置并重新构建。

~~~bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select autopatrol_robot --event-handlers console_direct+
source install/setup.bash
~~~

第三步：保持 Gazebo 和 Nav2 两个终端运行。如果旧的自动巡检 launch 仍在运行，先在它的终端按 Ctrl+C，然后重新启动：

~~~bash
ros2 launch autopatrol_robot autopatrol.launch.py
~~~

第四步：同时观察四类实验现象。

1. Gazebo：机器人先驶向 x=1.498、y=-5.898，再返回初始位置。
2. RViz：全局路径和局部路径出现，机器人模型沿路径移动。
3. 巡检终端：distance_remaining 逐渐减小；到达后出现 Navigation result: SUCCEEDED 和 Image saved。
4. 图片目录：每到达一个点新增一张 PNG。

~~~bash
ros2 topic echo /cmd_vel --no-daemon
~~~

另开终端执行上面的命令，可以观察机器人运动期间线速度和角速度变为非零；到达目标后速度回到零。

~~~bash
find /tmp/autopatrol_images -maxdepth 1 -type f -name '*.png' -printf '%TY-%Tm-%Td %TH:%TM:%TS %f\n' | sort
~~~

成功标准：机器人完成“前往目标点 → 到达拍照 → 返回起点 → 再次拍照”，最终输出 Configured patrol loops finished。

#### 7.5 扩展实验：RViz 跟随延迟优化

现场测量结果：

~~~text
/scan                 约 9.94 Hz
/odom                 约 29.25 Hz
/tf                   约 98 Hz
/local_costmap/costmap 约 1.67 Hz
/global_costmap/costmap 约 0.5 Hz
~~~

结论：雷达、里程计和 TF 频率正常。RViz 中看起来“跟不上”更可能来自代价地图发布频率偏低，以及 AMCL 更新门槛偏大，不应直接判定为 AMCL 算法失效。

已调整 fishbot_navigation2/config/nav2_params.yaml：

~~~yaml
amcl:
  ros__parameters:
    max_beams: 120
    update_min_a: 0.10
    update_min_d: 0.10

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 10.0
      publish_frequency: 5.0
~~~

修改已经构建完成。测试时保留 Gazebo，停止并重新启动 Nav2，再重新运行自动巡检：

~~~bash
source /opt/ros/humble/setup.bash
source /home/fishros/chapt6/chapt6_ws/install/setup.bash
ros2 launch fishbot_navigation2 navigation2.launch.py
~~~

另开终端测量优化后的频率：

~~~bash
ros2 topic hz /scan
ros2 topic hz /local_costmap/costmap
ros2 topic hz /global_costmap/costmap
~~~

jie_ware 技术评估：该项目是 ROS 1 catkin 包，依赖 roscpp、move_base_msgs 和旧版 tf。其 lidar_loc 使用小范围栅格穷举进行 scan-to-map 匹配，缺少 AMCL 的粒子分布、协方差与全局重定位能力，不直接并入当前 ROS 2 Humble/Nav2 主工程。

后续对比实验使用 ROS 2 原生的 slam_toolbox localization mode。当前系统已安装 localization_slam_toolbox_node，可以与 AMCL 做 A/B 测试，但应在本轮 Nav2 参数优化验证后单独进行，避免同时改变多个变量。

#### 7.5 地图、扫描与机器人错位的处理

Gazebo 显示 world 坐标，RViz 显示 map 坐标，画面中的绝对位置和朝向不要求相同。正确性应通过以下现象判断：

- 静态地图固定不动。
- RobotModel、LaserScan 和 local costmap 随机器人移动。
- LaserScan 的障碍点与静态地图墙体基本重合。

巡检程序此前每次启动都会把 AMCL 强制重设为固定起点。如果 Gazebo 机器人已经移动，但只重启 Nav2 或巡检程序，就会给 AMCL 一个错误的当前位姿，导致扫描、墙体和代价地图错位。

现已优化：

~~~yaml
reset_initial_pose_on_start: false
clear_costmaps_on_start: true
~~~

- 默认保留 AMCL 当前定位，不由业务应用反复重设位姿。
- 巡检启动并确认 Nav2 active 后，调用 Nav2 官方接口清理 local/global costmap，移除错误定位期间留下的障碍重影。
- 只有 Gazebo 刚刚重新生成机器人、机器人确实位于 initial_point 时，才临时把 reset_initial_pose_on_start 改为 true。

已经发生明显错位时，最可靠的恢复实验是完整重启：

~~~text
停止自动巡检 → 停止 Nav2 → 停止 Gazebo
→ 重新启动 Gazebo → 启动 Nav2 → 检查扫描与墙体
→ 启动自动巡检
~~~

如果不重启 Gazebo，则必须在 RViz 使用 2D Pose Estimate，把机器人当前真实位置和朝向重新告诉 AMCL，然后清理两张代价地图：

~~~bash
ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}"
ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}"
~~~

### 7.6 Git 仓库托管

本节对应的 GitHub 远程仓库已经创建：

~~~text
https://github.com/watermelon1412ye/ros2-study.git
~~~

2026-09-17 已只读验证该地址有效，目前没有远程分支，适合作为 7.6 的空仓库练习。

本地现状：main 分支尚无提交、尚未配置 origin，而且暂存区误加入了 build、install、log 和 Python 缓存等编译产物。不要直接执行 git commit 或 git push。7.6 应按下面顺序完成：

~~~text
编写 .gitignore
→ 清理暂存区但保留本地文件
→ 只暂存源码、配置、地图和学习文档
→ 检查提交内容
→ 创建第一次提交
→ 绑定 GitHub 仓库
→ 推送并在网页观察文件与提交记录
~~~

清理完成后的远程绑定与推送命令：

~~~bash
git remote add origin https://github.com/watermelon1412ye/ros2-study.git
git branch -M main
git push -u origin main
~~~

## 当前进度

- 7.2 建图流程与仿真环境优化：已完成。
- 7.3 Navigation 2 基础导航：已完成。
- 7.3 动态避障验证：已完成。
- 7.4 导航应用开发：已完成实测验证。
- 7.5 自动巡检机器人：已完成定点巡检实测，包含语音服务、巡检控制、图像保存。
- 7.6 Git 仓库托管：GitHub 空仓库地址已确认；本地暂存区需要先清理并补充 .gitignore，之后再提交和推送。
- 第 7 章自主导航：7.2 到 7.5 的定点实测已完成；下一步亲手完成 7.5 移动巡检实验，再进入 7.6 Git 托管实验。

## 当前工程状态

已具备：

- Gazebo 仿真环境。
- 干净建图世界 `clean_room.world`。
- 可用地图：
  - `src/fishbot_navigation2/maps/room.yaml`
  - `src/fishbot_navigation2/maps/room.pgm`
- Navigation 2 启动文件：
  - `src/fishbot_navigation2/launch/navigation2.launch.py`
- 建图启动文件：
  - `src/fishbot_navigation2/launch/mapping.launch.py`
- 应用开发包：
  - `src/fishbot_application`
- 自动巡检接口包：
  - `src/autopatrol_interfaces`
- 自动巡检应用包：
  - `src/autopatrol_robot`

## 已验证能力

- `/scan` 正常发布。
- `/odom` 正常发布。
- `/tf` 正常发布。
- Nav2 能加载地图。
- AMCL 定位正常。
- `Nav2 Goal` 单点导航正常。
- 临时障碍物避障正常。
- `fishbot_application` 包在 2026-09-16 再次构建成功。
- 以下 4 个应用节点已注册并实测：

```text
fishbot_application init_robot_pose
fishbot_application get_robot_pose
fishbot_application nav_to_pose
fishbot_application waypoint_follower
```

今日最终实测结果：

```text
init_robot_pose:
  Nav2 is active and AMCL initial pose was sent.

get_robot_pose:
  Robot pose in map: x=-0.427, y=-5.696, z=0.000, yaw=0.026 rad

nav_to_pose:
  Sent navigation goal: x=1.498, y=-5.898, yaw=1.692 rad
  Navigation result: SUCCEEDED

waypoint_follower:
  Sent 3 waypoint goals.
  Current waypoint index: 0
  Current waypoint index: 1
  Current waypoint index: 2
  Waypoint navigation result: SUCCEEDED
```

## 今日关键调整

`get_robot_pose`：

- 改为主循环 `rclpy.spin_once()` 处理 TF 消息。
- 使用 `Time(seconds=0.0)` 查询最新 TF。
- 默认使用仿真时间。
- 退出时避免重复 shutdown 报错。

`nav_to_pose` / `waypoint_follower`：

- 增加 Ctrl+C 时主动取消当前导航任务的处理。

`nav2_params.yaml`：

```text
general_goal_checker.yaw_goal_tolerance = 6.28
wait_at_waypoint.waypoint_pause_duration = 1
```

说明：

- 这两个参数是为了今天快速验证应用接口。
- 后续做真实巡检时，应重新选择实际可通行路点，并把 yaw 容差恢复到更严格的值。

## 第 7 章阶段总结

第 7 章主线：

```text
建图 -> 保存地图 -> 启动 Nav2 -> AMCL 定位 -> 单点导航 -> 动态避障 -> 应用程序调用导航接口 -> 路点巡检
```

必须掌握：

- 建图环境要干净，临时障碍物不能扫进静态地图。
- Nav2 实际读取安装目录中的地图、参数和 launch 资源。
- 修改 launch/config/maps 后要重新 `colcon build` 并重新 `source install/setup.bash`。
- Gazebo、SLAM、RViz、Nav2 要统一 `use_sim_time`。
- AMCL 初始位姿是 `map` 坐标系下的位置，不是 Gazebo 世界坐标。
- `map -> odom -> base_footprint` 是定位链路核心。
- Nav2 的最终控制输出是 `/cmd_vel`。
- 动态避障依赖 `/scan`、local costmap 和 controller server。
- `NavigateToPose` 负责单点导航，`FollowWaypoints` 负责多路点导航。
- Action 适合导航任务，因为它有 goal、feedback、result，并且可以取消。

## 7.4 常用命令

构建：

```bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select fishbot_navigation2 fishbot_application --event-handlers console_direct+
source install/setup.bash
```

启动 Gazebo：

```bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fishbot_description gazebo_sim.launch.py
```

启动 Nav2：

```bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fishbot_navigation2 navigation2.launch.py
```

验证应用节点：

```bash
ros2 run fishbot_application init_robot_pose
ros2 run fishbot_application get_robot_pose
ros2 run fishbot_application nav_to_pose
ros2 run fishbot_application waypoint_follower
```

关键检查：

```bash
ros2 pkg executables fishbot_application
ros2 node list
ros2 action list
ros2 action info /navigate_to_pose -t
ros2 action info /follow_waypoints -t
ros2 topic echo /cmd_vel --once --no-daemon
ros2 topic echo /amcl_pose --once --no-daemon
timeout 4 ros2 run tf2_ros tf2_echo map base_footprint
```

## 当前 AMCL 初始位姿

```text
x: -0.424
y: -5.680
yaw: 0.024
```

如果重新扫图、修改出生点或更换地图，需要重新校准这组值。

## 7.5 自动巡检机器人实测结果

已新增：

- `src/autopatrol_interfaces/srv/SpeachText.srv`
- `src/autopatrol_robot/autopatrol_robot/speaker.py`
- `src/autopatrol_robot/autopatrol_robot/patrol_node.py`
- `src/autopatrol_robot/config/patrol_config.yaml`
- `src/autopatrol_robot/launch/autopatrol.launch.py`

实测结果：

```text
speech_text service:
  espeakng unavailable; speech will be logged only.
  Speech completed: 正在初始化位置
  Speech completed: 位置初始化完成

patrol_node:
  Start patrol loop 1.
  Loaded target point 0/1/2.
  Target is the initial patrol point; mark reached.
  Image saved: /tmp/autopatrol_images/image_0.18_-0.20_7519118.png
  Image saved: /tmp/autopatrol_images/image_0.18_-0.20_7519271.png
  Image saved: /tmp/autopatrol_images/image_0.18_-0.20_7519290.png
  Configured patrol loops finished.
```

说明：

- 当前环境未安装 `espeakng`，所以语音节点使用日志兜底，不影响服务调用链路。
- 今日采用定点巡检验证 7.5 主流程；真实多点移动巡检需要重新选择地图内可通行目标点。

## 7.5 常用命令

构建：

```bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select autopatrol_interfaces autopatrol_robot --event-handlers console_direct+
source install/setup.bash
```

检查接口和可执行节点：

```bash
ros2 interface show autopatrol_interfaces/srv/SpeachText
ros2 pkg executables autopatrol_robot
ros2 launch autopatrol_robot autopatrol.launch.py --show-args
```

运行自动巡检：

```bash
ros2 launch autopatrol_robot autopatrol.launch.py
```

查看保存图片：

```bash
find /tmp/autopatrol_images -maxdepth 1 -type f -name '*.png' -printf '%f %s bytes\n'
```

## 7.6 当前状态

已完成：

- 添加 `src/README.md`，记录功能包、构建命令、导航启动命令、自动巡检命令和图片保存路径。

未执行：

- Gitee/GitHub 远程托管。原因是当前工作区 `.git` 目录异常，且没有远程仓库地址和账号认证信息。

后续如果要继续 7.6，应先确定使用 Gitee 还是 GitHub，然后在一个干净 Git 仓库中执行 `git init`、`git add`、`git commit`、`git remote add`、`git push`。
