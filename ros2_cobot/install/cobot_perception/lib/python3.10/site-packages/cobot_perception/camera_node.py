import rclpy
from rclpy.node import Node
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image


class CameraNode(Node):
    def __init__(self):
        # Define 'camera_node' for ros2 so it appears when running ros2 node list
        super().__init__('camera_node')

        self.publisher = self.create_publisher(Image, 'camera_frames', 10) #10 is a queue msg count. A buffer if a ros2 sub falls behind
        self.bridge = CvBridge()
        self.capture = cv2.VideoCapture(0)
        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback) # Like a mainloop for ROS2, tell it a frequency to execute 

    def timer_callback(self):
        success, frame = self.capture.read()
        
        # Handle failure to read from cam
        if not success:
            self.get_logger().warn('Failed to read frame from camera')
            return
        
        # Convert cv2 img reading to ROS2 format, then publish
        image_message = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        self.publisher.publish(image_message)


def main(args=None):
    rclpy.init()
    node = CameraNode()
    # Sping up the node. I think this is like threading.thred
    rclpy.spin(node)
    # Cleanup node once shutdown
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()