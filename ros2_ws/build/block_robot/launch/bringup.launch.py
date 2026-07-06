#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    rosbridge_launch = os.path.join(
        get_package_share_directory('rosbridge_server'),
        'launch',
        'rosbridge_websocket_launch.xml'
    )

    return LaunchDescription([
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(rosbridge_launch)
        ),
        Node(
            package='block_robot',
            executable='interpreter_node',
            name='interpreter_node',
            output='screen',
        ),
        Node(
            package='block_robot',
            executable='ultrasonic_node',
            name='ultrasonic_node',
            output='screen',
        ),
        Node(
            package='block_robot',
            executable='buzzer_node',
            name='buzzer_node',
            output='screen',
        ),
    ])
