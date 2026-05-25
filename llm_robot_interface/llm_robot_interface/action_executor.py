#!/usr/bin/env python3
import json
import subprocess
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ActionExecutor(Node):
    def __init__(self):
        super().__init__('action_executor')
        
        # Subscribe to LLM decisions
        self.sub = self.create_subscription(String, 'llm_action_out', self.on_action, 10)
        
        # Map objects to their specific ROS 2 python nodes
        self.sort_scripts = {
            "plastic": "sort_plastics.py",
            "metal":   "sort_metals.py",
            "glass":   "sort_glass.py"
        }

        self.get_logger().info('ActionExecutor Ready. Waiting for commands...')

    def on_action(self, msg):
        try:
            data = json.loads(msg.data)
            action = data.get("action")
            target_obj = data.get("object")
            explanation = data.get("explanation", "")

            # Log the reasoning (LLM explanation)
            if explanation:
                print(f"\n[ROBOT EXPLANATION]: {explanation}\n")

            # Handle Sorting
            if action == "sort" and target_obj in self.sort_scripts:
                script_name = self.sort_scripts[target_obj]
                self.get_logger().info(f"Command Validated. Running {script_name}...")
                
                # Execute the specific file
                # Assuming these files are in 'pymoveit2' package. Change if different.
                subprocess.Popen(["ros2", "run", "pymoveit2", script_name])
            
            elif action == "sort":
                 self.get_logger().warning(f"No sorting script found for object: {target_obj}")

        except Exception as e:
            self.get_logger().error(f"Execution Error: {e}")

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(ActionExecutor())
    rclpy.shutdown()

if __name__ == '__main__':
    main()