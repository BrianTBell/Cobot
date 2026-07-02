
"""
SPEECH TO TEXT PUBLISHER:

Speech to text class captures audio via sounddevice lib, passes it to whisper for speech to text, 
then published text to ros2 node. This is the robots ears more or less
"""

import rclpy
from rclpy.node import Node
from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np
from std_msgs.msg import String


class SpeechToTextNode(Node):
    """ Converts speech to text and publishes text to a ROS2 node. """
    def __init__(self):
        super().__init__('speech_to_text_node')
    
        self.publisher = self.create_publisher(String, 'speech_transcript', 10)
        self.model = WhisperModel('tiny', device='cpu', compute_type='int8')

        self.sampling_rate = 16000
        self.chunk_duration = 0.5
        self.silence_threshold = 0.001
        self.silence_limit = 1.0
        self.silence_elapsed = 0.0
        self.audio_buffer = []

        self.stream = sd.InputStream(
            samplerate=self.sampling_rate,
            channels=1,
            callback=self.audio_callback,
            blocksize=int(self.sampling_rate * self.chunk_duration),
        )
        self.stream.start()


    def audio_callback(self, indata, frames, time_info, status):
        """ Takes samples audio and appends it
        
        Args: 

        """
        volume = np.linalg.norm(indata) / len(indata)
        # If noise coming through append it.
        if volume > self.silence_threshold:
            self.audio_buffer.append(indata.copy())
            self.silence_elapsed = 0.0

        # Otherwise increment silence duration.
        else:
            self.silence_elapsed += self.chunk_duration

            # If silence duration > threshold, and audible noise was recorded, publish and reset. 
            if self.silence_elapsed > self.silence_limit and len(self.audio_buffer) > 0:
                try:
                    self.transcribe_and_publish()
                except:
                    self.get_logger().error(f'Trancsription failed {e}')
                self.audio_buffer = []
                self.silence_elapsed = 0.0


        
    def transcribe_and_publish(self):
        """ Transcibe collected audio and publish to ROS2 node. """
        # Stitch together chunks of audio recorded while talking (the buffer).
        audio_data = np.concatenate(self.audio_buffer, axis=0).flatten()

        # Transcribe & publish.
        segments, info = self.model.transcribe(audio_data, language='en')
        transcript_text = ' '.join(segment.text for segment in segments).strip()

        if transcript_text:
            message = String()
            message.data = transcript_text
            self.publisher.publish(message)
            self.get_logger().info(f'Publised transcript: {transcript_text}')



def main(args=None):
    """ Spin da node. """
    rclpy.init(args=args)
    node = SpeechToTextNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()



if __name__ == "__main__":
    main()
