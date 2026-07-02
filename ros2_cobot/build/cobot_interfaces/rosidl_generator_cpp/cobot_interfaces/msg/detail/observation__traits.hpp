// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from cobot_interfaces:msg/Observation.idl
// generated code does not contain a copyright notice

#ifndef COBOT_INTERFACES__MSG__DETAIL__OBSERVATION__TRAITS_HPP_
#define COBOT_INTERFACES__MSG__DETAIL__OBSERVATION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "cobot_interfaces/msg/detail/observation__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace cobot_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const Observation & msg,
  std::ostream & out)
{
  out << "{";
  // member: transcript
  {
    out << "transcript: ";
    rosidl_generator_traits::value_to_yaml(msg.transcript, out);
    out << ", ";
  }

  // member: transcript_confidence
  {
    out << "transcript_confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.transcript_confidence, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Observation & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: transcript
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "transcript: ";
    rosidl_generator_traits::value_to_yaml(msg.transcript, out);
    out << "\n";
  }

  // member: transcript_confidence
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "transcript_confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.transcript_confidence, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Observation & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace cobot_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use cobot_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const cobot_interfaces::msg::Observation & msg,
  std::ostream & out, size_t indentation = 0)
{
  cobot_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use cobot_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const cobot_interfaces::msg::Observation & msg)
{
  return cobot_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<cobot_interfaces::msg::Observation>()
{
  return "cobot_interfaces::msg::Observation";
}

template<>
inline const char * name<cobot_interfaces::msg::Observation>()
{
  return "cobot_interfaces/msg/Observation";
}

template<>
struct has_fixed_size<cobot_interfaces::msg::Observation>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<cobot_interfaces::msg::Observation>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<cobot_interfaces::msg::Observation>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // COBOT_INTERFACES__MSG__DETAIL__OBSERVATION__TRAITS_HPP_
