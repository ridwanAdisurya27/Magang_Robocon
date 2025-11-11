#!/usr/bin/env python3  
import rclpy
import subprocess
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity, DeleteEntity



class RespawnRobot(Node):
    def __init__(self):
        super().__init__('respawn_robot')
        # Delete existing entity if it exists
        self.del_cli = self.create_client(DeleteEntity, '/delete_entity')
        # async wait for the service to be available
        while not self.del_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /delete_entity service...')
        del_req = DeleteEntity.Request()
        del_req.name = "robot1"
        self.del_future = self.del_cli.call_async(del_req)
        rclpy.spin_until_future_complete(self, self.del_future)

        if self.del_future.result().success:
            self.get_logger().info("Old robot deleted successfully.")
        else:
            self.get_logger().warn("Delete failed or robot not found.")

        # Repawn the robot
        xacro_path = '/home/ridwan/alamak_gazebo/src/simulasi-2026/description/diff_drive_description.urdf.xacro'
        urdf_output = '/tmp/diff_drive_description.urdf'
        subprocess.run(['ros2', 'run', 'xacro', 'xacro', xacro_path, '-o', urdf_output], check=True)
        self.cli = self.create_client(SpawnEntity, '/spawn_entity')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn_entity service...')
        self.req = SpawnEntity.Request()
        self.req.name = "robot1"
        self.req.xml = open(urdf_output, 'r').read()
        self.req.initial_pose.position.x = 0.8
        self.req.initial_pose.position.y = 5.5
        self.req.initial_pose.position.z = 0.2

    def send_request(self):
        self.get_logger().info("Sending spawn request for robot1...")
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        if self.future.result() is not None:
            self.get_logger().info("Robot spawned successfully!")
        else:
            self.get_logger().error(f"Failed to spawn robot: {self.future.exception()}")


def main():
    rclpy.init()
    node = RespawnRobot()
    node.send_request()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
