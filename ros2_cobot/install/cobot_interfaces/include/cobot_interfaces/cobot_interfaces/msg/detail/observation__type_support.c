// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from cobot_interfaces:msg/Observation.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "cobot_interfaces/msg/detail/observation__rosidl_typesupport_introspection_c.h"
#include "cobot_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "cobot_interfaces/msg/detail/observation__functions.h"
#include "cobot_interfaces/msg/detail/observation__struct.h"


// Include directives for member types
// Member `transcript`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void cobot_interfaces__msg__Observation__rosidl_typesupport_introspection_c__Observation_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  cobot_interfaces__msg__Observation__init(message_memory);
}

void cobot_interfaces__msg__Observation__rosidl_typesupport_introspection_c__Observation_fini_function(void * message_memory)
{
  cobot_interfaces__msg__Observation__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember cobot_interfaces__msg__Observation__rosidl_typesupport_introspection_c__Observation_message_member_array[2] = {
  {
    "transcript",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(cobot_interfaces__msg__Observation, transcript),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "transcript_confidence",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(cobot_interfaces__msg__Observation, transcript_confidence),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers cobot_interfaces__msg__Observation__rosidl_typesupport_introspection_c__Observation_message_members = {
  "cobot_interfaces__msg",  // message namespace
  "Observation",  // message name
  2,  // number of fields
  sizeof(cobot_interfaces__msg__Observation),
  cobot_interfaces__msg__Observation__rosidl_typesupport_introspection_c__Observation_message_member_array,  // message members
  cobot_interfaces__msg__Observation__rosidl_typesupport_introspection_c__Observation_init_function,  // function to initialize message memory (memory has to be allocated)
  cobot_interfaces__msg__Observation__rosidl_typesupport_introspection_c__Observation_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t cobot_interfaces__msg__Observation__rosidl_typesupport_introspection_c__Observation_message_type_support_handle = {
  0,
  &cobot_interfaces__msg__Observation__rosidl_typesupport_introspection_c__Observation_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_cobot_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, cobot_interfaces, msg, Observation)() {
  if (!cobot_interfaces__msg__Observation__rosidl_typesupport_introspection_c__Observation_message_type_support_handle.typesupport_identifier) {
    cobot_interfaces__msg__Observation__rosidl_typesupport_introspection_c__Observation_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &cobot_interfaces__msg__Observation__rosidl_typesupport_introspection_c__Observation_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
