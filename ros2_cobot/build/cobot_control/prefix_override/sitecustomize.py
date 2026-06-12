import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/brian/Projects/Cobot/ros2_cobot/install/cobot_control'
