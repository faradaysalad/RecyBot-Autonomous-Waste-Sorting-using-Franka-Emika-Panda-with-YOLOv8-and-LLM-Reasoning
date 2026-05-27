from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. LLM Interface (The Brain)
        Node(
            package='llm_robot_interface',  # <--- CHANGE THIS to your actual package name
            executable='llm_interface_node',
            name='llm_interface',
            output='screen'
        ),
        
        # 2. Action Executor (The Hands)
        Node(
            package='llm_robot_interface',  # <--- CHANGE THIS to your actual package name
            executable='action_executor',
            name='action_executor',
            output='screen'
        ),
    ])