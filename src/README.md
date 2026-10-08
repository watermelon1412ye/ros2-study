# ROS 2 Chapter 7 Navigation Practice

本目录保存第 7 章自主导航相关功能包，覆盖建图、Nav2 导航、导航应用开发和自动巡检机器人实践。

## Packages

- `fishbot_description`：机器人模型、Gazebo 仿真与传感器。
- `fishbot_navigation2`：地图、Nav2 参数和导航启动文件。
- `fishbot_application`：7.4 导航应用节点，包括初始化位姿、读取位姿、单点导航和路点导航。
- `autopatrol_interfaces`：7.5 自动巡检语音服务接口。
- `autopatrol_robot`：7.5 自动巡检机器人节点，包括巡检控制、语音播报服务和图像记录。

## Build

```bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select fishbot_navigation2 fishbot_application autopatrol_interfaces autopatrol_robot --event-handlers console_direct+
source install/setup.bash
```

## Run Navigation

Terminal 1:

```bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fishbot_description gazebo_sim.launch.py
```

Terminal 2:

```bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fishbot_navigation2 navigation2.launch.py
```

## Run Autopatrol

Terminal 3:

```bash
cd /home/fishros/chapt6/chapt6_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch autopatrol_robot autopatrol.launch.py
```

Saved patrol images are written to:

```text
/tmp/autopatrol_images
```

Note: if `espeakng` is not installed, `speaker.py` keeps the service online and logs speech text so the patrol workflow can still be tested.
