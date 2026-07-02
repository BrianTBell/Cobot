// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from cobot_interfaces:msg/Observation.idl
// generated code does not contain a copyright notice

#ifndef COBOT_INTERFACES__MSG__DETAIL__OBSERVATION__STRUCT_H_
#define COBOT_INTERFACES__MSG__DETAIL__OBSERVATION__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'transcript'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/Observation in the package cobot_interfaces.
typedef struct cobot_interfaces__msg__Observation
{
  rosidl_runtime_c__String transcript;
  float transcript_confidence;
} cobot_interfaces__msg__Observation;

// Struct for a sequence of cobot_interfaces__msg__Observation.
typedef struct cobot_interfaces__msg__Observation__Sequence
{
  cobot_interfaces__msg__Observation * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} cobot_interfaces__msg__Observation__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // COBOT_INTERFACES__MSG__DETAIL__OBSERVATION__STRUCT_H_
