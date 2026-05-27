#!/usr/bin/env python3
"""
Pick and place node using fixed Cartesian coordinates for picking,
with multiple pre-pick joint configurations.
After grasping, robot moves to home position while keeping joint1
value from the pre-pick configuration.
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

        # Motion parameters
        self.moveit2.max_velocity = 0.1
        self.moveit2.max_acceleration = 0.1
        self.moveit2.planning_time = 5.0
        self.moveit2.max_planning_attempts = 10

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

        # Joint configurations
        self.start_joints = [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, math.radians(-125.0)
        ]

        self.home_joints = [
            0.0, 0.0, 0.0,
            math.radians(-90.0), 0.0,
            math.radians(92.0), math.radians(50.0)
        ]

        self.drop_joints = [math.radians(127.0), math.radians(57.0), math.radians(0.0),
                             math.radians(-52.0), math.radians(0.0), math.radians(153.0), math.radians(0.0)]

        # PRE-PICK JOINT POSITIONS
        self.pre_pick_joints_obj1 = [
            math.radians(-16), math.radians(0), math.radians(0),
            math.radians(-134), math.radians(0),
            math.radians(136), math.radians(-46)
        ]

        self.pre_pick_joints_obj2 = [
            math.radians(9), math.radians(20), math.radians(1),
            math.radians(-142), math.radians(21),
            math.radians(153), math.radians(69)
        ]

        # Pick pose
        self.pick_position = [0.6, 0.7, 0.45]
        self.quat_xyzw = [1.0, 0.0, 0.0, 0.0]

        self.execute_sequence()

    # ---------- HELPER ----------
    def home_with_joint1(self, joint1_value):
        joints = self.home_joints.copy()
        joints[0] = joint1_value
        return joints

    # ---------- MAIN SEQUENCE ----------
    def execute_sequence(self):
        self.get_logger().info("Starting pick-and-place sequence")

        # START
        self.moveit2.move_to_configuration(self.start_joints)
        self.moveit2.wait_until_executed()

        # MOVE TO HOME
        self.moveit2.move_to_configuration(self.home_joints)
        self.moveit2.wait_until_executed()

        self.moveit2.move_to_configuration(
            self.home_with_joint1(self.pre_pick_joints_obj1[0])
        )

        # ================= Glass 1 =================
        self.gripper.open()
        self.gripper.wait_until_executed()

        self.moveit2.move_to_configuration(self.pre_pick_joints_obj1)
        self.moveit2.wait_until_executed()

        self.gripper.close()
        self.gripper.wait_until_executed()

        self.moveit2.move_to_configuration(
            self.home_with_joint1(self.pre_pick_joints_obj1[0])
        )
        self.moveit2.wait_until_executed()

        self.moveit2.move_to_configuration(self.drop_joints)
        self.moveit2.wait_until_executed()

        self.gripper.open()
        self.gripper.wait_until_executed()

        self.gripper.close()
        self.gripper.wait_until_executed()

        self.moveit2.move_to_configuration(self.home_joints)
        self.moveit2.wait_until_executed()

        # ================= Glass 2 =================
        self.gripper.open()
        self.gripper.wait_until_executed()

        self.moveit2.move_to_configuration(self.pre_pick_joints_obj2)
        self.moveit2.wait_until_executed()

        self.gripper.close()
        self.gripper.wait_until_executed()

        self.moveit2.move_to_configuration(
            self.home_with_joint1(self.pre_pick_joints_obj2[0])
        )
        self.moveit2.wait_until_executed()

        self.moveit2.move_to_configuration(self.drop_joints)
        self.moveit2.wait_until_executed()

        self.gripper.open()
        self.gripper.wait_until_executed()

        self.gripper.close()
        self.gripper.wait_until_executed()

        # RETURN TO START
        self.moveit2.move_to_configuration(self.start_joints)
        self.moveit2.wait_until_executed()

        self.get_logger().info("Sequence complete. Shutting down.")
        rclpy.shutdown()


def main():
    rclpy.init()
    node = PickAndPlace()

    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
