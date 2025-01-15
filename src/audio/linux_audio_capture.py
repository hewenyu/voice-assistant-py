import pulsectl
import numpy as np

class LinuxAudioCapture:
    def __init__(self):
        self.pulse = pulsectl.Pulse('audio-capture')
        self.stream = None
        self.is_recording = False

    def list_applications(self):
        sink_inputs = self.pulse.sink_input_list()
        apps = []
        for sink in sink_inputs:
            app_info = {
                'index': sink.index,
                'name': sink.name,
                'application': sink.proplist.get('application.name', ''),
                'binary': sink.proplist.get('application.process.binary', ''),
                'pid': sink.proplist.get('application.process.id', '')
            }
            apps.append(app_info)
            print(f"Found application: {app_info}")
        return apps

    def capture_application(self, sink_index):
        try:
            # 获取对应的 sink
            sink_input = self.pulse.sink_input_info(sink_index)
            
            # 创建监听源
            monitor_source = self.pulse.get_sink_by_name(sink_input.sink).monitor_source
            
            # 设置录制流
            self.stream = self.pulse.stream_create(
                'audio-capture',
                rate=44100,
                channels=2,
                format='float32le',
                source=monitor_source
            )
            
            self.is_recording = True
            
            # 开始录制
            while self.is_recording:
                data = self.stream.read()
                if data:
                    self.process_audio(np.frombuffer(data, dtype=np.float32))
                    
        except Exception as e:
            print(f"Error capturing audio: {e}")
        finally:
            if self.stream:
                self.stream.disconnect()

    def stop_capture(self):
        self.is_recording = False

    def process_audio(self, audio_data):
        # 处理音频数据
        pass

    def cleanup(self):
        if self.pulse:
            self.pulse.close()