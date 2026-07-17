// TODO next session - deps to install on the Ubuntu setup
//       rclcpp, 
//       sensor_msgs, 
//       cv_bridge, 
//       OpenCV
//       Eigen3        (linear algebra, ORB-SLAM3 dependency)
//       Pangolin      (ORB-SLAM3's viewer)
//       DBoW2         (ORB-SLAM3's place-recognition dependency, bundled in its repo)
//       ORB-SLAM3     (build from source: https://github.com/UZ-SLAMLab/ORB_SLAM3)
// Also try to find a way to lock camera / level when running mono SLAM. Get intrinsics YAML figured out.

#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "cv_bridge/cv_bridge.h"
#include "opencv2/core.hpp"


class Orb3SlamNode : public rclcpp::Node
{
public:
  /* Subscribe to camera_frames node of camera_node.py*/
  Orb3SlamNode()
  : Node("orb3_slam_node")
  {
    subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
      "camera_frames",
      10,
      std::bind(&Orb3SlamNode::image_callback, this, std::placeholders::_1));
  }

private:

  void image_callback(const sensor_msgs::msg::Image::SharedPtr msg)
  {
    cv_bridge::CvImagePtr cv_ptr;
    try {
      cv_ptr = cv_bridge::toCvCopy(msg, "bgr8");
    } catch (const cv_bridge::Exception & e) {
      RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
      return;
    }

    RCLCPP_INFO(
      this->get_logger(), "Got frame: %dx%d",
      cv_ptr->image.cols, cv_ptr->image.rows);
  }

  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Orb3SlamNode>());
  rclcpp::shutdown();
  return 0;
}
