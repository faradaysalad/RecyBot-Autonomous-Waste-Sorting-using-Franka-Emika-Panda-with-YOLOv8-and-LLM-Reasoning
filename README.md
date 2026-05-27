# RecyBot: Autonomous Waste Sorting using Franka Emika Panda with YOLOv8, MoveIt 2, and LLM Reasoning

## Overview

RecyBot is an intelligent autonomous robotic system designed to detect, classify, and sort recyclable waste.  
This project integrates deep learning-based computer vision, advanced robotic motion planning, and Large Language Model (LLM) reasoning to operate a Franka Emika Panda robotic arm within a simulated Gazebo environment.

Initially developed using YOLOv8 and MoveIt 2 for automated pick-and-place operations, the system was later enhanced with LLaMA 3.1 to support natural language interaction between the user and the robot.

The robot is capable of:
- Understanding flexible human commands
- Detecting and classifying recyclable objects
- Performing autonomous pick-and-place actions
- Providing explainable reasoning for its decisions

---

# Key Features

## Real-Time Object Detection
- Utilizes YOLOv8 trained on the Garbage Classification dataset
- Detects 6 material categories:
  - Cardboard
  - Glass
  - Metal
  - Paper
  - Plastic
  - Biodegradable / Background

## Advanced Motion Planning
- Uses MoveIt 2 for:
  - Inverse kinematics
  - Motion planning
  - Collision avoidance
  - Cartesian trajectory execution

## Natural Language Interaction
- Powered by LLaMA 3.1 through Ollama
- Allows flexible commands such as:
  - `"Sort the plastics"`
  - `"Pick up the metal can"`
  - `"What objects do you see?"`

## Explainable AI (XAI)
- Provides reasoning behind object classification
- Uses:
  - YOLO confidence scores
  - Geometric features
  - Bounding box observations
  - Surface texture descriptions

## Modular ROS 2 Architecture
- Separates:
  - High-level LLM reasoning
  - Low-level robotic control
- Improves safety and maintainability

---

# System Architecture

The system consists of several interconnected ROS 2 nodes.

## `yolobot_recognition`
Responsible for:
- Running YOLOv8 inference
- Receiving camera input
- Publishing detected objects using custom `yolo_msgs`

## `llm_interface_node`
Acts as the cognitive reasoning layer:
- Receives user prompts
- Reads YOLO detections
- Sends prompts to LLaMA 3.1
- Produces structured JSON action commands

## `action_executor`
Responsible for:
- Receiving parsed commands
- Selecting target objects
- Executing robot movement
- Performing grasp and drop actions

## `chat_terminal`
Provides:
- Interactive terminal-based communication
- Natural language interface with the robot

---

# Technologies Used

## Robotics & Simulation
- ROS 2 Humble
- MoveIt 2
- Gazebo / Ignition Gazebo
- RViz2

## AI & Vision
- YOLOv8
- OpenCV
- PyTorch

## LLM Integration
- LLaMA 3.1
- Ollama

## Robot Platform
- Franka Emika Panda 7DOF Robot Arm

---

# Dataset & Model Performance

The YOLOv8 model was trained for 100 epochs using the Garbage Classification dataset containing over 10,000 images.

## Performance Highlights
| Class | mAP@0.5 |
|------|------|
| Glass | 0.787 |
| Metal | 0.693 |
| Overall | 0.520 |

The model achieved strong performance on common recyclable materials, enabling reliable grasping and sorting operations.

---

# Project Structure

```bash
RecyBot/
├── src/
│   ├── yolobot_recognition/
│   ├── llm_robot_interface/
│   ├── action_executor/
│   ├── panda_bringup/
│   └── yolo_msgs/
│
├── models/
├── worlds/
├── launch/
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone <your-repository-url>
cd RecyBot
```

## Build Workspace

```bash
colcon build --symlink-install
source install/setup.bash
```

---

# How to Run

## 1. Launch Robot & Simulation

```bash
ros2 launch panda_bringup pick_and_place.launch.py
```

This launches:
- Ignition Gazebo
- Panda robot
- RViz2 visualization

---

## 2. Start the LLM Brain & Action Executor

```bash
ros2 launch llm_robot_interface brain.launch.py
```

This starts:
- `llm_interface_node`
- `action_executor`

---

## 3. Start the Chat Interface

```bash
ros2 run llm_robot_interface chat_terminal
```

You can now communicate with RecyBot through the terminal.

---

# Baseline Test (Without LLM)

To test the original rigid pick-and-place pipeline without natural language reasoning:

```bash
ros2 run pymoveit2 pick_and_place2.py
```

---

# Example Commands

## Scene Understanding

```text
What do you see?
```

Returns:
- Detected objects
- Object categories
- Confidence scores

---

## Explainable Reasoning

```text
Why is that a box?
```

Returns:
- Geometric observations
- Shape reasoning
- Confidence-based explanations

---

## Autonomous Sorting

```text
Can you sort the metals please?
```

Triggers:
- Object selection
- Motion planning
- Pick-and-place execution

---

# Future Improvements

- Real-world deployment using physical Panda robot
- Voice-based interaction
- Multi-object simultaneous sorting
- Improved YOLO accuracy
- Reinforcement learning for adaptive grasping
- Multi-camera perception system

---

# Authors

Developed for the **TTTC3413 Robot Applications** course at  
Faculty of Information Science and Technology (FTSM),  
Universiti Kebangsaan Malaysia (UKM).

## Contributor

- Farah Dania Binti Imam Nawawi (A205566)

---

# Acknowledgements

Special thanks to:
- Faculty of Information Science and Technology (FTSM UKM)
- Robot Applications Course (TTTC3413)
- Open-source ROS 2 community
- Ultralytics YOLOv8 developers
- MoveIt 2 contributors
- Ollama & Meta LLaMA developers

---

# License

This project is developed for academic and research purposes.
