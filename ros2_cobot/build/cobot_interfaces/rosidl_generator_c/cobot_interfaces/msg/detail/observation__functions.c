// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from cobot_interfaces:msg/Observation.idl
// generated code does not contain a copyright notice
#include "cobot_interfaces/msg/detail/observation__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `transcript`
#include "rosidl_runtime_c/string_functions.h"

bool
cobot_interfaces__msg__Observation__init(cobot_interfaces__msg__Observation * msg)
{
  if (!msg) {
    return false;
  }
  // transcript
  if (!rosidl_runtime_c__String__init(&msg->transcript)) {
    cobot_interfaces__msg__Observation__fini(msg);
    return false;
  }
  // transcript_confidence
  return true;
}

void
cobot_interfaces__msg__Observation__fini(cobot_interfaces__msg__Observation * msg)
{
  if (!msg) {
    return;
  }
  // transcript
  rosidl_runtime_c__String__fini(&msg->transcript);
  // transcript_confidence
}

bool
cobot_interfaces__msg__Observation__are_equal(const cobot_interfaces__msg__Observation * lhs, const cobot_interfaces__msg__Observation * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // transcript
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->transcript), &(rhs->transcript)))
  {
    return false;
  }
  // transcript_confidence
  if (lhs->transcript_confidence != rhs->transcript_confidence) {
    return false;
  }
  return true;
}

bool
cobot_interfaces__msg__Observation__copy(
  const cobot_interfaces__msg__Observation * input,
  cobot_interfaces__msg__Observation * output)
{
  if (!input || !output) {
    return false;
  }
  // transcript
  if (!rosidl_runtime_c__String__copy(
      &(input->transcript), &(output->transcript)))
  {
    return false;
  }
  // transcript_confidence
  output->transcript_confidence = input->transcript_confidence;
  return true;
}

cobot_interfaces__msg__Observation *
cobot_interfaces__msg__Observation__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  cobot_interfaces__msg__Observation * msg = (cobot_interfaces__msg__Observation *)allocator.allocate(sizeof(cobot_interfaces__msg__Observation), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(cobot_interfaces__msg__Observation));
  bool success = cobot_interfaces__msg__Observation__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
cobot_interfaces__msg__Observation__destroy(cobot_interfaces__msg__Observation * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    cobot_interfaces__msg__Observation__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
cobot_interfaces__msg__Observation__Sequence__init(cobot_interfaces__msg__Observation__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  cobot_interfaces__msg__Observation * data = NULL;

  if (size) {
    data = (cobot_interfaces__msg__Observation *)allocator.zero_allocate(size, sizeof(cobot_interfaces__msg__Observation), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = cobot_interfaces__msg__Observation__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        cobot_interfaces__msg__Observation__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
cobot_interfaces__msg__Observation__Sequence__fini(cobot_interfaces__msg__Observation__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      cobot_interfaces__msg__Observation__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

cobot_interfaces__msg__Observation__Sequence *
cobot_interfaces__msg__Observation__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  cobot_interfaces__msg__Observation__Sequence * array = (cobot_interfaces__msg__Observation__Sequence *)allocator.allocate(sizeof(cobot_interfaces__msg__Observation__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = cobot_interfaces__msg__Observation__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
cobot_interfaces__msg__Observation__Sequence__destroy(cobot_interfaces__msg__Observation__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    cobot_interfaces__msg__Observation__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
cobot_interfaces__msg__Observation__Sequence__are_equal(const cobot_interfaces__msg__Observation__Sequence * lhs, const cobot_interfaces__msg__Observation__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!cobot_interfaces__msg__Observation__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
cobot_interfaces__msg__Observation__Sequence__copy(
  const cobot_interfaces__msg__Observation__Sequence * input,
  cobot_interfaces__msg__Observation__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(cobot_interfaces__msg__Observation);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    cobot_interfaces__msg__Observation * data =
      (cobot_interfaces__msg__Observation *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!cobot_interfaces__msg__Observation__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          cobot_interfaces__msg__Observation__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!cobot_interfaces__msg__Observation__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
