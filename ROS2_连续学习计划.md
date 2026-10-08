# ROS 2 连续学习计划

记录日期：2026-09-15

当前教材：《ROS 2 机器人开发：从入门到实践》（鱼香 ROS / 小鱼）

当前进度：第 7 章 7.4，已经完成 7.2 建图、7.3 Navigation 2 基础导航与避障验证，正在学习“导航应用开发指南”。

## 今日学习启动

今天继续第 7 章 7.4，不开新坑。重点不是多写代码，而是验证应用程序和 Nav2 的接口链路：

```text
/initialpose -> TF -> /navigate_to_pose -> /follow_waypoints
```

今日完成标准：

- 至少跑通 `init_robot_pose` 和 `get_robot_pose`。
- 如果时间够，再跑通 `nav_to_pose` 和 `waypoint_follower`。
- 每跑一个命令，都在 `notes/ROS2_第7章_自主导航学习日志.md` 记录现象、成功标准和失败排查。
- 今天结束时更新 `ROS2_学习进度与命令速查.md` 的“当前进度”和“下次继续”。

## 一、总体目标

目标不是“把书看完”，而是把 ROS 2 变成能独立调试、能独立做项目的工具。

阶段目标：

1. 第 7 章：让仿真机器人稳定完成建图、导航、动态避障、路点导航和自动巡检。
2. 第 8 章：理解 Nav2 插件机制，能替换规划器和控制器。
3. 第 9 章：建立实体移动机器人开发的整体认识，重点理解底盘控制、里程计、micro-ROS、雷达和导航。
4. 第 10 章：补齐 ROS 2 进阶能力，包括 QoS、执行器、回调组、生命周期节点、组件和 DDS。

## 二、学习节奏

每天上班学习约 2 小时，下班学习约 3 小时，总计约 5 小时。建议不要全部用来“推进新内容”，否则很容易卡住后疲劳。

推荐分配：

- 上班 2 小时：读书 + 跑通一个小目标 + 记录关键命令。
- 下班 3 小时：动手复现 + 解决白天遗留问题 + 整理日志。

每天固定流程：

1. 10 分钟：回看昨天日志，只看“下一步”和“卡点”。
2. 30-45 分钟：阅读当前小节，先理解输入、输出、节点、话题、参数。
3. 60-90 分钟：按书中步骤动手跑通。
4. 30-60 分钟：调试、验证、截图或保存关键输出。
5. 20 分钟：写学习日志，只写今天真正验证过的内容。

关键命令记录规则：

- 启动类命令写完整环境准备：`cd`、`source`、`ros2 launch`。
- 验证类命令写清楚检查对象：Topic、TF、Action、参数或节点。
- 每个关键命令下面补一句“为什么运行它”。
- 命令输出很长时，只记录能证明成功或失败的关键 3-8 行。

## 三、章节推进方式

建议按“小节学习，大阶段复盘”。

原因：

- ROS 2 每个小节通常对应一个可运行实验，小节粒度最适合验证。
- 大章节内容太多，容易变成“看过了但没跑通”。
- 每完成一个大章节，再做一次复盘，把散落的命令、节点、话题、参数串起来。

执行规则：

- 一个小节的完成标准不是“看完”，而是至少跑通一次关键命令。
- 一个大章节的完成标准是能画出系统结构，说明数据从哪里来、到哪里去。
- 卡住超过 30 分钟，先记录现象，再用最小命令验证，不要一直盯着 RViz 或 Gazebo 猜。

## 四、当前第 7 章计划

### 7.3 Navigation 2

状态：已完成。

目标：启动 Nav2，加载 `room.yaml`，在 RViz 中设置初始位姿并发送导航目标点。

必须掌握：

- Nav2 的输入：`/tf`、地图、雷达、目标点。
- Nav2 的输出：`/cmd_vel`。
- 关键模块：BT 导航服务器、规划器服务器、控制器服务器、恢复器服务器。
- 关键参数：`robot_base_frame`、`robot_radius`、`max_vel_theta`、`acc_lim_theta`、`inflation_radius`、`xy_goal_tolerance`、`yaw_goal_tolerance`。

关键命令：

```bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fishbot_description gazebo_sim.launch.py
```

```bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fishbot_navigation2 navigation2.launch.py
```

验证命令：

```bash
ros2 topic list
ros2 topic echo /cmd_vel --once
ros2 action list
ros2 node list
```

完成标准：

- RViz 正确显示地图。已完成。
- 使用 `2D Pose Estimate` 或 AMCL 自动初始位姿后，机器人定位正常。已完成。
- 使用 `Nav2 Goal` 后机器人能规划路径并移动。已完成。
- `/cmd_vel` 能看到 Nav2 发布的速度指令。已完成。
- Gazebo 中添加临时障碍物后，小车可以自动绕行。已完成。

### 7.4 导航应用开发

状态：进行中，代码已加入工程，下一步是逐个运行验证。

目标：理解用话题、TF、Action 接口调用导航，而不是只依赖 RViz 按钮。

重点：

- 用话题初始化机器人位姿。
- 用 TF 获取机器人实时位置。
- 用 `/navigate_to_pose` 进行单点导航。
- 用 `/follow_waypoints` 进行路点导航。

关键命令：

```bash
ros2 action info /navigate_to_pose -t
ros2 interface show nav2_msgs/action/NavigateToPose
```

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 2, y: 2}, orientation: {w: 1.0}}}}" --feedback
```

```bash
ros2 action info /follow_waypoints -t
ros2 interface show nav2_msgs/action/FollowWaypoints
```

完成标准：

- 能说清楚 Action 的 goal、feedback、result。
- 能用命令行发送一个导航目标。
- 能运行 `init_robot_pose` 初始化机器人位姿。
- 能运行 `get_robot_pose` 输出 `map -> base_footprint`。
- 能运行 `nav_to_pose` 完成单点导航。
- 能运行 `waypoint_follower` 完成多路点导航。
- 能理解 `BasicNavigator` 封装了 Nav2 Action 客户端。

### 7.5 自动巡检机器人

目标：把导航、参数、语音、相机图像保存串成一个小项目。

重点：

- 巡检控制节点。
- 导航点参数化。
- 到点后语音播报。
- 订阅相机图像并保存。

完成标准：

- 机器人能按多个目标点循环移动。
- 到达目标点后能执行附加动作。
- 日志中记录系统架构：参数、服务、话题、Action 分别承担什么。

### 7.6 Git 仓库托管

目标：把当前学习工程管理起来，避免后续改坏后无法回退。

重点命令：

```bash
git status
git init
git add .
git commit -m "记录第7章导航学习工程"
```

如果当前目录不是 Git 仓库，先不要着急提交，等本章阶段稳定后再统一整理。

## 五、后续章节节奏

### 第 8 章：插件机制与自定义导航

建议用 5-7 天。

学习重点：

- `pluginlib` 的插件注册与加载。
- 自定义规划器插件。
- 自定义控制器插件。
- 修改 Nav2 参数，让 Nav2 加载自己的插件。

本章不要追求算法很强，先追求“插件能被 Nav2 加载并运行”。

### 第 9 章：实体机器人

建议用 10-14 天。

学习重点：

- 机器人系统结构：传感器、执行器、决策系统。
- 电机控制、编码器、PID、运动学正逆解。
- 里程计计算。
- micro-ROS 接入 ROS 2。
- 实体机器人建图和导航流程。

如果手头没有实体硬件，可以先把系统框架、控制链路、消息接口学明白。

### 第 10 章：ROS 2 进阶

建议用 7-10 天。

学习重点：

- QoS：为什么有些话题订阅不到。
- 执行器与回调组：为什么回调会阻塞。
- 生命周期节点：Nav2 为什么有 `configure`、`activate` 等状态。
- 组件：多个节点如何组合到同一进程。
- DDS：局域网通信和中间件配置。

## 六、学习日志写作规范

现在采用“一个章节一个主日志 + 一个当前状态快照”的方式，不再按每天或每个小节拆很多 `.md` 文件。

文件职责：

- `ROS2_学习进度与命令速查.md`：记录各章当前进度、今天入口、下次继续，以及按小节整理的关键命令。
- `notes/ROS2_第7章_自主导航学习日志.md`：写详细学习过程、命令解释、验证结果和排错。
- `notes/ROS2_学习日志写作规范.md`：写长期可复用的日志模板和记录方法。
- `ROS2_连续学习计划.md`：写章节节奏、阶段目标和学习习惯。

当前规则：

```text
notes/ROS2_第7章_自主导航学习日志.md
```

后续第 8、9、10 章也按同样方式组织：

```text
notes/ROS2_第8章_Nav2插件机制学习日志.md
notes/ROS2_第9章_实体机器人学习日志.md
notes/ROS2_第10章_ROS2进阶学习日志.md
```

统一写作规范见：

```text
notes/ROS2_学习日志写作规范.md
```

每个小节固定写：

```text
本节目标 -> 前置条件 -> 核心概念 -> 操作流程 -> 关键代码 -> 验证方法 -> 常见问题 -> 图解 -> 主动回忆 -> 本节结论
```

## 七、书中内容摘录与截图规则

摘录原则：

- 只摘关键定义、关键流程、参数含义，不整段搬书。
- 摘录后必须写一句“我自己的理解”。
- 图要优先截系统架构图、节点通信图、参数配置图、RViz/Gazebo 运行结果图。

适合摘录的内容类型：

- ROS 2 / Nav2 / ros2_control 的架构解释。
- 参数含义，例如地图 `resolution`、`origin`、`occupied_thresh`、`free_thresh`。
- 关键接口，例如 `/navigate_to_pose`、`/follow_waypoints`。
- 书中总结性的句子。

当前第 7 章可先摘录这一句并写理解：

> Navigation 2 的目标是让机器人安全地从 A 点移动到 B 点。

我的理解：Nav2 不是单个算法，而是一整套导航框架，它把定位、地图、规划、控制、恢复行为组合起来，最后输出 `/cmd_vel` 控制机器人。

截图建议：

- `7-8 Navigation2 系统框架`：理解 Nav2 输入、输出和内部服务器。
- `7-9 RViz 中导航相关按钮`：记录 `2D Pose Estimate` 和 `Nav2 Goal`。
- `7-10 初始化完成后的地图`：记录初始位姿设置后的状态。
- `7-20 动态绕障重新规划路径`：记录 Nav2 动态避障效果。
- `7-26 巡检机器人系统架构`：记录小项目的节点关系。

截图保存建议：

```text
notes/assets/chapt7/
```

可以按这个命名：

```text
7-3-nav2-architecture.png
7-3-rviz-pose-goal.png
7-3-costmap-after-init.png
7-3-dynamic-obstacle.png
7-5-patrol-system.png
```

## 八、卡住时的处理流程

卡住不要硬熬，按下面顺序查：

1. 进程是否启动：`ros2 node list`
2. 话题是否存在：`ros2 topic list`
3. 话题是否有数据：`ros2 topic echo <topic> --once`
4. TF 是否连通：RViz Fixed Frame 是否正确，是否有 `map -> odom -> base_footprint/base_link`
5. 参数是否安装到 `install`：改完 `config`、`launch`、`maps` 后是否重新 `colcon build`
6. 是否 source 了环境：`source /opt/ros/humble/setup.bash` 和 `source install/setup.bash`
7. 仿真时间是否一致：Nav2、RViz、Gazebo 是否都使用 `use_sim_time:=True`

每次排查只改一个变量，改完立刻验证。

## 九、连续学习习惯

每天只要求完成一个“可验证结果”，不要追求一天吃掉很多小节。

最低完成标准：

- 今天跑通过一个命令。
- 今天记录了一个现象。
- 今天解决或定位了一个问题。

如果当天状态不好，也做 20 分钟维护型学习：

- 整理昨天日志。
- 复跑一个已经成功的 launch。
- 看一个节点的参数。
- 画一张话题/节点关系图。

连续学习靠的是不断降低重启成本。每天结束时一定写“下次继续”，第二天直接照着做。
