import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class Cobot(Node):
    def __init__(self):
        super().__init__('cobot')
        self.bridge = CvBridge()
        self.create_subscription(Image, 'camera/image_raw', self.view_camera, 1)

    def view_camera(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        cv2.imshow('Camera Feed', frame)
        if cv2.waitKey(1) == ord("q"):
            rclpy.shutdown()


def main():
    rclpy.init()
    node = Cobot()
    rclpy.spin(node)
    node.destroy_node()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
