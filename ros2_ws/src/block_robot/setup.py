from setuptools import find_packages, setup

package_name = 'block_robot'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/bringup.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robot',
    maintainer_email='robot@example.com',
    description='block coding robot interpreter/ultrasonic/buzzer nodes',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'interpreter_node = block_robot.interpreter_node:main',
            'ultrasonic_node = block_robot.ultrasonic_node:main',
            'buzzer_node = block_robot.buzzer_node:main',
        ],
    },
)
