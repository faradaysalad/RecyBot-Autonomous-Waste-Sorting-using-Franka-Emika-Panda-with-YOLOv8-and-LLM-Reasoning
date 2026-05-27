#!/usr/bin/env python3
import sys
import threading
import json
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.executors import ExternalShutdownException

class ChatTerminal(Node):
    def __init__(self):
        super().__init__('chat_terminal')

        # Publisher: Sends your text to the LLM
        self.pub = self.create_publisher(String, 'llm_text_in', 10)

        # Subscriber: Listens for the LLM's response
        self.sub = self.create_subscription(String, 'llm_action_out', self.on_response, 10)
        
        # Event to control the thinking animation thread
        self.stop_thinking_event = threading.Event()
        self.thinking_thread = None
        
        print("-------------------------------------------------")
        print("🤖 ROBOT CHAT TERMINAL READY")
        print("   Type your command and press Enter.")
        print("   (Ctrl+C to quit)")
        print("-------------------------------------------------")

    def animate_thinking(self):
        """Prints a 'Thinking...' message with cycling dots."""
        dots = ["   ", ".  ", ".. ", "..."]
        idx = 0
        while not self.stop_thinking_event.is_set():
            sys.stdout.write(f"\r🤖 Thinking{dots[idx % 4]}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.4)
        
        # --- THIS PART HANDLES THE CLEANUP AND NEW LINE ---
        # 1. Clear the "Thinking..." text with spaces
        sys.stdout.write("\r" + " " * 30 + "\r")
        
        # 2. Add a newline explicitly so the answer starts below
        sys.stdout.write("\n") 
        sys.stdout.flush()
        # --------------------------------------------------

    def on_response(self, msg):
        try:
            # Signal the animation thread to stop
            self.stop_thinking_event.set()
            
            # Wait for the animation to finish clearing the line
            if self.thinking_thread and self.thinking_thread.is_alive():
                self.thinking_thread.join()
            
            # Parse the JSON from the robot
            data = json.loads(msg.data)
            explanation = data.get("explanation", "No explanation provided.")
            action = data.get("action", "unknown")
            
            # Print the robot's reply
            # The animate_thinking function has already pushed us to a new line
            print(f"🤖 Robot: {explanation}")
            
            if action != "unknown":
                print(f"   [Action Triggered: {action.upper()}]")
            
            print("-" * 50)
            
            # Restart the input loop
            self.prompt_user()
            
        except Exception as e:
            self.stop_thinking_event.set()
            print(f"Error parsing response: {e}")

    def prompt_user(self):
        threading.Thread(target=self.get_input, daemon=True).start()

    def get_input(self):
        try:
            user_text = input("\n👉 You: ")
            
            if user_text.strip() == "":
                self.prompt_user()
                return

            # Start the "Thinking..." animation
            self.stop_thinking_event.clear()
            self.thinking_thread = threading.Thread(target=self.animate_thinking, daemon=True)
            self.thinking_thread.start()
            
            # Publish to ROS
            msg = String()
            msg.data = user_text
            self.pub.publish(msg)
            
        except (EOFError, KeyboardInterrupt):
            pass

def main(args=None):
    rclpy.init(args=args)
    node = ChatTerminal()
    node.prompt_user()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        print("\n\nExiting... Goodbye!")
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()