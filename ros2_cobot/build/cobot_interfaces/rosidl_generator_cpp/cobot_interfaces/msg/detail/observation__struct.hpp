// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from cobot_interfaces:msg/Observation.idl
// generated code does not contain a copyright notice

#ifndef COBOT_INTERFACES__MSG__DETAIL__OBSERVATION__STRUCT_HPP_
#define COBOT_INTERFACES__MSG__DETAIL__OBSERVATION__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__cobot_interfaces__msg__Observation __attribute__((deprecated))
#else
# define DEPRECATED__cobot_interfaces__msg__Observation __declspec(deprecated)
#endif

namespace cobot_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Observation_
{
  using Type = Observation_<ContainerAllocator>;

  explicit Observation_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->transcript = "";
      this->transcript_confidence = 0.0f;
    }
  }

  explicit Observation_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : transcript(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->transcript = "";
      this->transcript_confidence = 0.0f;
    }
  }

  // field types and members
  using _transcript_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _transcript_type transcript;
  using _transcript_confidence_type =
    float;
  _transcript_confidence_type transcript_confidence;

  // setters for named parameter idiom
  Type & set__transcript(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->transcript = _arg;
    return *this;
  }
  Type & set__transcript_confidence(
    const float & _arg)
  {
    this->transcript_confidence = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    cobot_interfaces::msg::Observation_<ContainerAllocator> *;
  using ConstRawPtr =
    const cobot_interfaces::msg::Observation_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<cobot_interfaces::msg::Observation_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<cobot_interfaces::msg::Observation_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      cobot_interfaces::msg::Observation_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<cobot_interfaces::msg::Observation_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      cobot_interfaces::msg::Observation_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<cobot_interfaces::msg::Observation_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<cobot_interfaces::msg::Observation_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<cobot_interfaces::msg::Observation_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__cobot_interfaces__msg__Observation
    std::shared_ptr<cobot_interfaces::msg::Observation_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__cobot_interfaces__msg__Observation
    std::shared_ptr<cobot_interfaces::msg::Observation_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Observation_ & other) const
  {
    if (this->transcript != other.transcript) {
      return false;
    }
    if (this->transcript_confidence != other.transcript_confidence) {
      return false;
    }
    return true;
  }
  bool operator!=(const Observation_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Observation_

// alias to use template instance with default allocator
using Observation =
  cobot_interfaces::msg::Observation_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace cobot_interfaces

#endif  // COBOT_INTERFACES__MSG__DETAIL__OBSERVATION__STRUCT_HPP_
