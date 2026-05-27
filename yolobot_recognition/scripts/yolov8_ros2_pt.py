#!/usr/bin/env python3
import os
import json
from ultralytics import YOLO
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from ament_index_python.packages import get_package_share_directory

class CameraSubscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber')

        # Load Model
        try:
            model_path = os.path.join(
                get_package_share_directory('yolobot_recognition'),
                'scripts', 'best.pt')
            self.model = YOLO(os.path.expanduser(model_path), verbose=False)
        except Exception as e:
            self.get_logger().error(f"Model load failed: {e}")
            raise

        self.bridge = CvBridge()
        
        # Subscriber & Publisher
        self.subscription = self.create_subscription(
            Image, '/camera/image_raw', self.camera_callback, 10)
        
        # Publish structured JSON data now
        self.text_pub = self.create_publisher(String, '/yolo_detection', 10)
        self.img_pub = self.create_publisher(Image, '/inference_result', 1)

    def camera_callback(self, msg):
        try:
            img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            results = self.model(img, verbose=False)
        except Exception:
            return

        detected_objects = []

        for r in results:
            for box in r.boxes:
                # 1. Basic Info
                cls_id = int(box.cls[0])
                name = self.model.names[cls_id]
                conf = float(box.conf[0])
                
                # 2. Geometric Reasoning (Bounding Box)
                # box.xywh returns: [center_x, center_y, width, height]
                x, y, w, h = box.xywh[0].tolist()
                
                aspect_ratio = h / w
                shape_desc = "unknown"
                if aspect_ratio > 1.5:
                    shape_desc = "elongated/tall"
                elif aspect_ratio < 0.8:
                    shape_desc = "wide/flat"
                else:
                    shape_desc = "compact/square"

                # 3. Pack into Dictionary
                obj_data = {
                    "class": name,
                    "confidence": f"{conf:.2f}",
                    "geometry": {
                        "aspect_ratio": f"{aspect_ratio:.2f}",
                        "shape": shape_desc,
                        "width": int(w),
                        "height": int(h)
                    }
                }
                detected_objects.append(obj_data)

        # Publish JSON string
        msg_str = String()
        msg_str.data = json.dumps(detected_objects)
        self.text_pub.publish(msg_str)

        # Debug image
        annotated = results[0].plot()
        self.img_pub.publish(self.bridge.cv2_to_imgmsg(annotated, 'bgr8'))

def main(args=None):
    rclpy.init(args=args)
    node = CameraSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()