# ROS 2 自主导航与自动巡检机器人

本项目记录 ROS 2 Humble 第 7 章的自主导航实践，包括 Gazebo 仿真、SLAM 建图、Navigation 2 导航、导航应用开发和自动巡检机器人。

## 功能包

- `fishbot_description`：机器人模型、Gazebo 仿真和传感器配置。
- `fishbot_navigation2`：地图、Navigation 2 参数以及建图和导航启动文件。
- `fishbot_application`：初始化位姿、读取位姿、单点导航和路点导航节点。
- `autopatrol_interfaces`：自动巡检使用的语音服务接口。
- `autopatrol_robot`：巡检控制、语音播报和相机图像记录节点。

## 开发环境

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo
- Navigation 2
- slam_toolbox

## 安装依赖

```bash
sudo apt update
sudo apt install -y \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-gazebo-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-xacro \
  ros-humble-cv-bridge \
  ros-humble-tf-transformations \
  espeak-ng \
  python3-opencv \
  python3-pip

python3 -m pip install --user espeakng transforms3d
```

## 构建

```bash
cd ~/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
colcon build --event-handlers console_direct+
source install/setup.bash
```

## 运行

终端 1，启动 Gazebo：

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fishbot_description gazebo_sim.launch.py
```

终端 2，启动 Navigation 2：

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fishbot_navigation2 navigation2.launch.py
```

终端 3，启动自动巡检：

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch autopatrol_robot autopatrol.launch.py
```

巡检图片默认保存在 `/tmp/autopatrol_images`。

## 作者

- [watermelon1412ye](https://github.com/watermelon1412ye)
