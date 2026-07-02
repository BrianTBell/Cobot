// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from cobot_interfaces:msg/Observation.idl
// generated code does not contain a copyright notice

#ifndef COBOT_INTERFACES__MSG__DETAIL__OBSERVATION__BUILDER_HPP_
#define COBOT_INTERFACES__MSG__DETAIL__OBSERVATION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "cobot_interfaces/msg/detail/observation__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace cobot_interfaces
{

namespace msg
{

namespace builder
{

class Init_Observation_transcript_confidence
{
public:
  explicit Init_Observation_transcript_confidence(::cobot_interfaces::msg::Observation & msg)
  : msg_(msg)
  {}
  ::cobot_interfaces::msg::Observation transcript_confidence(::cobot_interfaces::msg::Observation::_transcript_confidence_type arg)
  {
    msg_.transcript_confidence = std::move(arg);
    return std::move(msg_);
  }

private:
  ::cobot_interfaces::msg::Observation msg_;
};

class Init_Observation_transcript
{
public:
  Init_Observation_transcript()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Observation_transcript_confidence transcript(::cobot_interfaces::msg::Observation::_transcript_type arg)
  {
    msg_.transcript = std::move(arg);
    return Init_Observation_transcript_confidence(msg_);
  }

private:
  ::cobot_interfaces::msg::Observation msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::cobot_interfaces::msg::Observation>()
{
  return cobot_interfaces::msg::builder::Init_Observation_transcript();
}

}  // namespace cobot_interfaces

#endif  // COBOT_INTERFACES__MSG__DETAIL__OBSERVATION__BUILDER_HPP_
