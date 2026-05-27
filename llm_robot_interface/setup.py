import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'llm_robot_interface'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Register the package in the ament index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        
        # Include package.xml
        ('share/' + package_name, ['package.xml']),
        
        # --- NEW: Include all launch files from the 'launch' folder ---
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        
        (os.path.join('share', package_name, 'llm_robot_interface'), glob('llm_robot_interface/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='fai',
    maintainer_email='fai@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Make sure these file names match your actual python files in the folder!
            'llm_interface_node = llm_robot_interface.llm_interface_node:main',
            'action_executor = llm_robot_interface.action_executor:main',
            
            # Optional: Add the chat terminal here too if you want to run it via ros2 run
            'chat_terminal = llm_robot_interface.chat_terminal:main',
        ],
    },
)
