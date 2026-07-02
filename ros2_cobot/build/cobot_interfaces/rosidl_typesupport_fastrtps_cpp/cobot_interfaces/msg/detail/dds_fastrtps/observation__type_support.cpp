// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from cobot_interfaces:msg/Observation.idl
// generated code does not contain a copyright notice
#include "cobot_interfaces/msg/detail/observation__rosidl_typesupport_fastrtps_cpp.hpp"
#include "cobot_interfaces/msg/detail/observation__struct.hpp"

#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions

namespace cobot_interfaces
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_cobot_interfaces
cdr_serialize(
  const cobot_interfaces::msg::Observation & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: transcript
  cdr << ros_message.transcript;
  // Member: transcript_confidence
  cdr << ros_message.transcript_confidence;
  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_cobot_interfaces
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  cobot_interfaces::msg::Observation & ros_message)
{
  // Member: transcript
  cdr >> ros_message.transcript;

  // Member: transcript_confidence
  cdr >> ros_message.transcript_confidence;

  return true;
}  // NOLINT(readability/fn_size)

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_cobot_interfaces
get_serialized_size(
  const cobot_interfaces::msg::Observation & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: transcript
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.transcript.size() + 1);
  // Member: transcript_confidence
  {
    size_t item_size = sizeof(ros_message.transcript_confidence);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_cobot_interfaces
max_serialized_size_Observation(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;


  // Member: transcript
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Member: transcript_confidence
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = cobot_interfaces::msg::Observation;
    is_plain =
      (
      offsetof(DataType, transcript_confidence) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static bool _Observation__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const cobot_interfaces::msg::Observation *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _Observation__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<cobot_interfaces::msg::Observation *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _Observation__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const cobot_interfaces::msg::Observation *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _Observation__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_Observation(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _Observation__callbacks = {
  "cobot_interfaces::msg",
  "Observation",
  _Observation__cdr_serialize,
  _Observation__cdr_deserialize,
  _Observation__get_serialized_size,
  _Observation__max_serialized_size
};

static rosidl_message_type_support_t _Observation__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_Observation__callbacks,
  get_message_typesupport_handle_function,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace cobot_interfaces

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_cobot_interfaces
const rosidl_message_type_support_t *
get_message_type_support_handle<cobot_interfaces::msg::Observation>()
{
  return &cobot_interfaces::msg::typesupport_fastrtps_cpp::_Observation__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, cobot_interfaces, msg, Observation)() {
  return &cobot_interfaces::msg::typesupport_fastrtps_cpp::_Observation__handle;
}

#ifdef __cplusplus
}
#endif
