#!/usr/bin/env python3
import math
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped


class SemiAutoNavigator(Node):
    def __init__(self):
        super().__init__('semi_auto_navigator')
        self.action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Lokasi file koordinat
        self.file_path = '/home/ridwan/alamak_gazebo/src/simulasi-2026/path/zones.txt'

    def read_targets(self):
        targets = []
        with open(self.file_path, 'r') as f:
            for line in f:
                if line.strip():
                    x, y, yaw = map(float, line.strip().split())
                    targets.append((x, y, yaw))
        return targets

    def quaternion_from_yaw(self, yaw):
        qz = math.sin(yaw / 2.0)
        qw = math.cos(yaw / 2.0)
        return qz, qw

    async def navigate_to_pose(self, x, y, yaw):
        qz, qw = self.quaternion_from_yaw(yaw)

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw

        self.get_logger().info(f'Navigating to: x={x:.2f}, y={y:.2f}, yaw={yaw:.2f}')

        await self.action_client.wait_for_server()
        send_goal_future = self.action_client.send_goal_async(goal_msg)
        goal_handle = await send_goal_future
        if not goal_handle.accepted:
            self.get_logger().warn(' Goal rejected')
            return
        self.get_logger().info(' Goal accepted')

        result_future = goal_handle.get_result_async()
        result = await result_future
        self.get_logger().info(' Goal reached!')

    async def run(self):
        targets = self.read_targets()
        for i, (x, y, yaw) in enumerate(targets):
            self.get_logger().info(f'\n=== Menuju Zona {i+1} ===')
            await self.navigate_to_pose(x, y, yaw)
            time.sleep(2)  # Delay kecil antar target


def main(args=None):
    rclpy.init(args=args)
    node = SemiAutoNavigator()
    rclpy.spin_until_future_complete(node, node.run())
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
