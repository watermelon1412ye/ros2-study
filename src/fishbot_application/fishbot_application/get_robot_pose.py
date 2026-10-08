import time  # 导入 time 模块，用于程序中的时间间隔判断

import rclpy  # 导入 ROS 2 Python 客户端库
from rclpy.executors import ExternalShutdownException  # 导入外部关闭异常，用于处理 ROS 2 被外部终止的情况
from rclpy.node import Node  # 导入 Node 类，所有 ROS 2 节点都需要继承这个类
from rclpy.parameter import Parameter  # 导入 Parameter 类，用于设置 ROS 2 节点参数
from rclpy.time import Time  # 导入 ROS 2 的 Time 类，用于指定 TF 查询时间
from tf2_ros import Buffer, TransformListener  # 导入 TF 缓冲区 Buffer 和 TF 监听器 TransformListener

from fishbot_application.utils import quaternion_to_yaw  # 导入自定义函数，将四元数转换为 yaw 偏航角


class TFListener(Node):  # 定义 TFListener 类，并继承 ROS 2 的 Node 类

    def __init__(self):  # 类的构造函数，在创建 TFListener 对象时自动执行

        super().__init__(  # 调用父类 Node 的构造函数，完成 ROS 2 节点初始化

            'fishbot_pose_listener',  # 设置当前 ROS 2 节点名称为 fishbot_pose_listener

            parameter_overrides=[  # 设置节点启动时需要覆盖的参数

                Parameter(  # 创建一个 ROS 2 参数对象

                    'use_sim_time',  # 参数名称，表示是否使用仿真时间

                    Parameter.Type.BOOL,  # 指定参数类型为布尔类型

                    True,  # 设置参数值为 True，表示使用仿真时间
                ),
            ],
        )

        # 创建 TF 缓冲区
        # Buffer 用来保存系统中最近一段时间内接收到的 TF 坐标变换数据
        self.buffer = Buffer(node=self)  # 将当前节点传入 Buffer，创建 TF 数据缓存对象

        # 创建 TF 监听器
        # TransformListener 会监听 /tf 和 /tf_static 等 TF 相关话题
        # 接收到的 TF 数据会自动存储到上面的 self.buffer 中
        self.listener = TransformListener(  # 创建 TransformListener 对象

            self.buffer,  # 指定 TF 数据保存到哪个 Buffer 中

            self,  # 指定该监听器属于当前 ROS 2 节点
        )

    def get_transform(self):  # 定义获取 TF 坐标变换的方法

        try:  # 尝试获取 TF，如果获取失败则进入 except

            # 从 TF 缓冲区中查询两个坐标系之间的变换关系
            tf = self.buffer.lookup_transform(

                'map',  # 目标坐标系：地图坐标系 map

                'base_footprint',  # 源坐标系：机器人底盘投影坐标系 base_footprint

                Time(  # 创建一个 ROS 2 时间对象

                    seconds=0.0  # 时间为 0，表示获取当前 TF 缓冲区中最新可用的变换
                ),
            )

        except Exception as exc:  # 如果 TF 查询过程中出现任何异常

            self.get_logger().warn(  # 使用 ROS 2 日志系统输出警告信息

                f'Cannot get map -> base_footprint TF: {exc}'  # 输出 TF 获取失败的原因
            )

            return  # 结束本次 get_transform() 函数调用

        # tf 是一个 TransformStamped 类型的数据
        # tf.transform 中保存真正的平移和旋转信息
        transform = tf.transform  # 提取 TF 中的 transform 变换数据

        # transform.rotation 是四元数形式的机器人姿态
        # quaternion_to_yaw() 将四元数转换为 yaw 偏航角
        yaw = quaternion_to_yaw(  # 调用四元数转 yaw 函数

            transform.rotation  # 将机器人旋转四元数传入函数
        )

        # 输出机器人当前在 map 坐标系下的位置和方向
        self.get_logger().info(

            'Robot pose in map: '  # 日志开头，说明输出的是机器人在 map 坐标系下的位姿

            f'x={transform.translation.x:.3f}, '  # 输出机器人 X 坐标，保留 3 位小数

            f'y={transform.translation.y:.3f}, '  # 输出机器人 Y 坐标，保留 3 位小数

            f'z={transform.translation.z:.3f}, '  # 输出机器人 Z 坐标，保留 3 位小数

            f'yaw={yaw:.3f} rad'  # 输出机器人 yaw 朝向角，单位为弧度 rad
        )


def main():  # 定义程序主函数

    rclpy.init()  # 初始化 ROS 2 Python 通信系统

    node = TFListener()  # 创建 TFListener 节点对象，同时执行 __init__() 初始化

    try:  # 尝试正常运行 ROS 2 节点

        last_print_time = 0.0  # 记录上一次打印机器人位姿的时间，初始值设置为 0

        while rclpy.ok():  # 只要 ROS 2 系统仍处于正常运行状态，就一直循环

            rclpy.spin_once(  # 执行一次 ROS 2 事件循环

                node,  # 指定需要处理回调的 ROS 2 节点

                timeout_sec=0.1  # 最长等待 0.1 秒，没有事件时也会返回
            )

            # spin_once 的作用很重要
            # TFListener 监听到的 /tf 数据需要 ROS 2 回调机制处理
            # 所以必须不断执行 spin_once，TF Buffer 才会持续更新

            now = time.monotonic()  # 获取当前单调时钟时间，用于计算时间间隔

            # monotonic() 适合做时间差计算
            # 因为它不会受到系统时间被手动修改的影响

            if now - last_print_time >= 1.0:  # 如果距离上一次打印已经超过 1 秒

                node.get_transform()  # 查询 map 到 base_footprint 的 TF，并打印机器人位姿

                last_print_time = now  # 更新上一次打印时间为当前时间

    except (  # 捕获程序退出过程中可能出现的异常

        KeyboardInterrupt,  # 用户按下 Ctrl+C 时产生的异常

        ExternalShutdownException  # ROS 2 被外部系统关闭时产生的异常

    ):

        pass  # 不进行额外处理，让程序正常进入资源释放流程

    node.destroy_node()  # 销毁 ROS 2 节点，释放节点相关资源

    if rclpy.ok():  # 判断 ROS 2 当前是否仍然处于初始化状态s

        rclpy.shutdown()  # 正式关闭 ROS 2 Python 通信系统


if __name__ == '__main__':  # 判断当前文件是否是直接运行，而不是被其他 Python 文件导入

    main()  # 调用 main() 主函数，启动整个程序