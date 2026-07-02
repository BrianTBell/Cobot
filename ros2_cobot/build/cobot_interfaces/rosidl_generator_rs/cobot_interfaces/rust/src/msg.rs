#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to cobot_interfaces__msg__Observation

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Observation {

    // This member is not documented.
    #[allow(missing_docs)]
    pub transcript: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub transcript_confidence: f32,

}



impl Default for Observation {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Observation::default())
  }
}

impl rosidl_runtime_rs::Message for Observation {
  type RmwMsg = super::msg::rmw::Observation;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        transcript: msg.transcript.as_str().into(),
        transcript_confidence: msg.transcript_confidence,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        transcript: msg.transcript.as_str().into(),
      transcript_confidence: msg.transcript_confidence,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      transcript: msg.transcript.to_string(),
      transcript_confidence: msg.transcript_confidence,
    }
  }
}


