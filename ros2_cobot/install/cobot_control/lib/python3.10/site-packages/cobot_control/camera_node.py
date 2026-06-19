import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')
        self.pub = self.create_publisher(Image, 'camera/image_raw', 1)
        self.bridge = CvBridge()
        self.cap = cv2.VideoCapture(0)
        self.timer = self.create_timer(0.033, self.tick)

    def tick(self):
        ret, frame = self.cap.read()
        if ret:
            self.pub.publish(self.bridge.cv2_to_imgmsg(frame, 'bgr8'))

    def destroy_node(self):
        self.cap.release()
        super.destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
