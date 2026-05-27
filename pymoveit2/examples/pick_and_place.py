#!/usr/bin/env python3
"""
Pick and place node using fixed Cartesian coordinates for picking,
with a pre-pick joint configuration for stable grasping.
No collision objects or attachments are used.
"""

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from pymoveit2 import MoveIt2, GripperInterface
from pymoveit2.robots import panda
import math

class PickAndPlace(Node):
    def __init__(self):
        super().__init__("pick_and_place_simple")

        self.callback_group = ReentrantCallbackGroup()

        # MoveIt2 arm interface
        self.moveit2 = MoveIt2(
            node=self,
            joint_names=panda.joint_names(),
            base_link_name=panda.base_link_name(),
            end_effector_name=panda.end_effector_name(),
            group_name=panda.MOVE_GROUP_ARM,
            callback_group=self.callback_group,
        )

        # Smoother motion
        self.moveit2.max_velocity = 0.6
        self.moveit2.max_acceleration = 0.6
        self.moveit2.planning_time = 2.0
        self.moveit2.max_planning_attempts = 5

        # Gripper
        self.gripper = GripperInterface(
            node=self,
            gripper_joint_names=panda.gripper_joint_names(),
            open_gripper_joint_positions=panda.OPEN_GRIPPER_JOINT_POSITIONS,
            closed_gripper_joint_positions=panda.CLOSED_GRIPPER_JOINT_POSITIONS,
            gripper_group_name=panda.MOVE_GROUP_GRIPPER,
            callback_group=self.callback_group,
            gripper_command_action_name="gripper_action_controller/gripper_cmd",
        )

        # Predefined joint positions (radians)
        self.start_joints = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, math.radians(-125.0)]
        self.home_joints  = [0.0, 0.0, 0.0, math.radians(-90.0), 0.0, math.radians(92.0), math.radians(50.0)]
        self.drop_joints  = [math.radians(155.0), math.radians(16.0), math.radians(1.0),
                             math.radians(-108.0), math.radians(-6.0), math.radians(127.0), math.radians(42.0)]

        # PRE-PICK joint configuration
        self.pre_pick_joints = [math.radians(0), math.radians(40), math.radians(0), math.radians(-90), math.radians(0), math.radians(131), math.radians(50)]

        # Pick coordinates
        self.pick_position = [0.6, 0.7, 0.45]
        self.approach_offset = 0.05
        self.quat_xyzw = [1.0, 0.0, 0.0, 0.0]  # top-down

        self.execute_sequence()

    def execute_sequence(self):
        self.get_logger().info("Starting pick-and-place motion...")

        # Move to start
        self.moveit2.move_to_configuration(self.start_joints)
        self.moveit2.wait_until_executed()

        # Move home
        self.moveit2.move_to_configuration(self.home_joints)
        self.moveit2.wait_until_executed()

        # Move above pick position
        self.moveit2.move_to_pose(position=self.pick_position, quat_xyzw=self.quat_xyzw)
        self.moveit2.wait_until_executed()

        # Open gripper
        self.gripper.open()
        self.gripper.wait_until_executed()

        # Move to pre-pick joint configuration
        self.get_logger().info("Moving to pre-pick joint configuration before grasping")
        self.moveit2.move_to_configuration(self.pre_pick_joints)
        self.moveit2.wait_until_executed()

        # Close gripper to pick object
        self.gripper.close()
        self.gripper.wait_until_executed()

        # Lift back to pick_position
        self.moveit2.move_to_pose(position=self.pick_position, quat_xyzw=self.quat_xyzw)
        self.moveit2.wait_until_executed()

        # Go home
        self.moveit2.move_to_configuration(self.home_joints)
        self.moveit2.wait_until_executed()

        # Move to drop area
        self.moveit2.move_to_configuration(self.drop_joints)
        self.moveit2.wait_until_executed()

        # Open gripper to release
        self.gripper.open()
        self.gripper.wait_until_executed()

        # Close gripper (reset)
        self.gripper.close()
        self.gripper.wait_until_executed()

        # Return to start
        self.moveit2.move_to_configuration(self.start_joints)
        self.moveit2.wait_until_executed()

        self.get_logger().info("Pick-and-place sequence complete. Shutting down.")
        rclpy.shutdown()


def main():
    rclpy.init()
    node = PickAndPlace()

    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()

