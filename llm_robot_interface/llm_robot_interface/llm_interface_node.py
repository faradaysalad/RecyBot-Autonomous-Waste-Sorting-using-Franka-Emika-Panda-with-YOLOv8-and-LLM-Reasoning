#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import requests

class LLMInterface(Node):
    def __init__(self):
        super().__init__('llm_interface')

        # Subscribe to user prompt
        self.sub_prompt = self.create_subscription(
            String, 'llm_text_in', self.prompt_callback, 10
        )

        # Subscribe to YOLO detections
        self.sub_detection = self.create_subscription(
            String, '/yolo_detection', self.detection_callback, 10
        )

        # Publish parsed actions
        self.pub_action = self.create_publisher(
            String, 'llm_action_out', 10
        )

        self.current_data = []
        self.model_name = "llama3.1"

        # Expanded Knowledge Base
        self.material_traits = {
            "plastic": (
                "General: Translucent or semi-opaque surfaces. "
                "Context: On the table, we see plastic bottles (cylindrical, transparent) "
                "or supplement vekas (white, opaque)."
            ),
            "metal": (
                "General: Shiny, reflective surface, rigid structure. "
                "Context: On the table, this is a **beverage can**. "
                "It is cylindrical with a metallic glint and an opening tab."
            ),
            "glass": (
                "General: Transparent surface with sharp reflective highlights. "
                "Context: These are glass bottles (green, wine-red, or clear)."
            ),
            "cardboard": (
                "General: Matte brown surface, fibrous texture. "
                "Context: It is a box/container. We see rectangular geometry."
            ),
            "paper": (
                "General: Thin, matte surface, often white. "
                "Context: Lightweight, crumpled or flat, often with text."
            )
        }

        self.get_logger().info("LLM Interface Node started (Enhanced)")

    def detection_callback(self, msg):
        try:
            self.current_data = json.loads(msg.data)
        except Exception:
            self.current_data = []

    def describe_scene_simple(self):
        """Fast path for 'what do you see' to avoid LLM latency."""
        if not self.current_data:
            return "I do not see any objects right now."

        counts = {}
        for obj in self.current_data:
            cls = obj["class"]
            counts[cls] = counts.get(cls, 0) + 1

        parts = []
        for cls, count in counts.items():
            name = cls if count == 1 else cls + "s"
            parts.append(f"{count} {name}")

        return "There is " + ", ".join(parts) + " on the table."

    def get_vision_context(self):
        if not self.current_data:
            return "Vision System: No objects detected."

        summary = "Vision System Detected Objects:\n"
        for i, obj in enumerate(self.current_data):
            name = obj["class"]
            conf = float(obj["confidence"]) * 100
            
            # Extract Geometry
            bbox_info = ""
            if "box" in obj:
                b = obj["box"]
                w, h = b[2]-b[0], b[3]-b[1]
                bbox_info = f"(Geometry: Bounding Box {w:.0f}x{h:.0f})"

            traits = self.material_traits.get(name, "Standard properties.")
            
            summary += (
                f"{i+1}. CLASS: {name.upper()}\n"
                f"   - Confidence: {conf:.1f}%\n"
                f"   - Context Info: {traits}\n"
                f"   - {bbox_info}\n"
            )
        return summary

    def prompt_callback(self, msg):
        user_prompt = msg.data.lower()
        self.get_logger().info(f"User prompt: {user_prompt}")

        # 1. SIMPLE QUERY HANDLING
        if "what do you see" in user_prompt or "on the table" in user_prompt:
            explanation = self.describe_scene_simple()
            self.pub_action.publish(String(data=json.dumps({
                "action": "none", "object": "", "explanation": explanation
            })))
            return

        # 2. CONSTRUCT SYSTEM PROMPT
        vision_context = self.get_vision_context()
        
        system_instruction = (
            "You are a RecyBot (Intelligent Waste Sorter).\n"
            "You have access to real-time YOLOv8 vision data and a knowledge base.\n\n"
            f"{vision_context}\n\n"
            "INSTRUCTIONS:\n"
            "1. **Synonym Mapping**: If user asks about a 'can', they mean 'METAL'. "
            "If 'box', they mean 'CARDBOARD'. If 'bottle', check 'PLASTIC' or 'GLASS'.\n"
            "2. **Why questions** (e.g., 'Why is that a can?'):\n"
            "   - Answer: 'I classified it as a can (Metal) because it has [High Confidence%] "
            "and fits the visual profile: [describe shiny/cylindrical traits]'.\n"
            "   - Mention that other classes were detected but had lower probability.\n"
            "3. **Property descriptions**: Always describe the object using the 'Context Info' provided above "
            "(e.g., mention the supplement vekas for plastic, or green color for glass).\n"
            "4. **Sorting**: If asked to sort, output JSON with action='sort'.\n"
        )

        # 3. QUERY LLM
        llm_response = self.call_ollama(system_instruction, user_prompt)

        # 4. PARSE & PUBLISH
        parsed = self.parse_response(user_prompt, llm_response)
        self.pub_action.publish(String(data=json.dumps(parsed)))

    def call_ollama(self, system, user):
        url = "http://localhost:11434/api/chat"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "stream": False
        }
        try:
            response = requests.post(url, json=payload)
            return response.json()["message"]["content"]
        except Exception:
            return "I am having trouble connecting to Ollama."

    def parse_response(self, user_prompt, llm_text):
        result = {
            "action": "none",
            "object": "",
            "explanation": llm_text
        }
        
        # Python Logic for Action Safety
        if "pick" in user_prompt or "sort" in user_prompt:
            result["action"] = "sort"
            # Map synonyms to classes for the action executor
            if "plastic" in user_prompt or "bottle" in user_prompt and "glass" not in user_prompt:
                result["object"] = "plastic"
            elif "metal" in user_prompt or "can" in user_prompt:
                result["object"] = "metal"
            elif "glass" in user_prompt:
                result["object"] = "glass"
            elif "cardboard" in user_prompt or "box" in user_prompt:
                result["object"] = "cardboard"
            elif "paper" in user_prompt:
                result["object"] = "paper"

        return result

def main(args=None):
    rclpy.init(args=args)
    node = LLMInterface()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()