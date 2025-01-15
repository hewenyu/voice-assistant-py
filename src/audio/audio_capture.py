import sounddevice as sd
import numpy as np

class AudioCapture:
    def __init__(self):
        self.stream = None
        self.is_recording = False
        self.sample_rate = 16000
        self.channels = 1

    def list_devices(self):
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            print(f"Device {i}: {device['name']}")
            print(f"  Channels: {device['max_input_channels']}/{device['max_output_channels']}")
            print(f"  Sample Rate: {device['default_samplerate']}")

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        # 处理音频数据
        audio_data = np.copy(indata)
        self.process_audio(audio_data)

    def start_recording(self, device_id=None):
        try:
            self.stream = sd.InputStream(
                device=device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self.callback
            )
            self.stream.start()
            self.is_recording = True
        except Exception as e:
            print(f"Error starting recording: {e}")

    def stop_recording(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.is_recording = False

    def process_audio(self, audio_data):
        # 在这里处理音频数据
        pass