from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='cobot_control', executable='camera_node'),
        Node(package='cobot_control', executable='camera_view'),
    ])
