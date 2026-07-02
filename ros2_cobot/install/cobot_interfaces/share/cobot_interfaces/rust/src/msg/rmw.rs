#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "cobot_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__cobot_interfaces__msg__Observation() -> *const std::ffi::c_void;
}

#[link(name = "cobot_interfaces__rosidl_generator_c")]
extern "C" {
    fn cobot_interfaces__msg__Observation__init(msg: *mut Observation) -> bool;
    fn cobot_interfaces__msg__Observation__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Observation>, size: usize) -> bool;
    fn cobot_interfaces__msg__Observation__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Observation>);
    fn cobot_interfaces__msg__Observation__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Observation>, out_seq: *mut rosidl_runtime_rs::Sequence<Observation>) -> bool;
}

// Corresponds to cobot_interfaces__msg__Observation
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Observation {

    // This member is not documented.
    #[allow(missing_docs)]
    pub transcript: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub transcript_confidence: f32,

}



impl Default for Observation {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !cobot_interfaces__msg__Observation__init(&mut msg as *mut _) {
        panic!("Call to cobot_interfaces__msg__Observation__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Observation {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { cobot_interfaces__msg__Observation__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { cobot_interfaces__msg__Observation__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { cobot_interfaces__msg__Observation__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Observation {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Observation where Self: Sized {
  const TYPE_NAME: &'static str = "cobot_interfaces/msg/Observation";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__cobot_interfaces__msg__Observation() }
  }
}


