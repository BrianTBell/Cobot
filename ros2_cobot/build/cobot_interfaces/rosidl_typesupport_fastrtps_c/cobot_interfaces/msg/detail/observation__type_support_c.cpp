// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from cobot_interfaces:msg/Observation.idl
// generated code does not contain a copyright notice
#include "cobot_interfaces/msg/detail/observation__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "cobot_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "cobot_interfaces/msg/detail/observation__struct.h"
#include "cobot_interfaces/msg/detail/observation__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "rosidl_runtime_c/string.h"  // transcript
#include "rosidl_runtime_c/string_functions.h"  // transcript

// forward declare type support functions


using _Observation__ros_msg_type = cobot_interfaces__msg__Observation;

static bool _Observation__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _Observation__ros_msg_type * ros_message = static_cast<const _Observation__ros_msg_type *>(untyped_ros_message);
  // Field name: transcript
  {
    const rosidl_runtime_c__String * str = &ros_message->transcript;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: transcript_confidence
  {
    cdr << ros_message->transcript_confidence;
  }

  return true;
}

static bool _Observation__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _Observation__ros_msg_type * ros_message = static_cast<_Observation__ros_msg_type *>(untyped_ros_message);
  // Field name: transcript
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->transcript.data) {
      rosidl_runtime_c__String__init(&ros_message->transcript);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->transcript,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'transcript'\n");
      return false;
    }
  }

  // Field name: transcript_confidence
  {
    cdr >> ros_message->transcript_confidence;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_cobot_interfaces
size_t get_serialized_size_cobot_interfaces__msg__Observation(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Observation__ros_msg_type * ros_message = static_cast<const _Observation__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name transcript
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->transcript.size + 1);
  // field.name transcript_confidence
  {
    size_t item_size = sizeof(ros_message->transcript_confidence);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _Observation__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_cobot_interfaces__msg__Observation(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_cobot_interfaces
size_t max_serialized_size_cobot_interfaces__msg__Observation(
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

  // member: transcript
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
  // member: transcript_confidence
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
    using DataType = cobot_interfaces__msg__Observation;
    is_plain =
      (
      offsetof(DataType, transcript_confidence) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _Observation__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_cobot_interfaces__msg__Observation(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Observation = {
  "cobot_interfaces::msg",
  "Observation",
  _Observation__cdr_serialize,
  _Observation__cdr_deserialize,
  _Observation__get_serialized_size,
  _Observation__max_serialized_size
};

static rosidl_message_type_support_t _Observation__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Observation,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, cobot_interfaces, msg, Observation)() {
  return &_Observation__type_support;
}

#if defined(__cplusplus)
}
#endif
