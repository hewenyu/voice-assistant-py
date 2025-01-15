import pulsectl
import numpy as np
import time

class LinuxAudioCapture:
    def __init__(self):
        self.pulse = pulsectl.Pulse('audio-capture')
        self.stream = None
        self.is_recording = False

    def list_applications(self):
        print("\nListing all PulseAudio sink inputs...")
        sink_inputs = self.pulse.sink_input_list()
        
        if not sink_inputs:
            print("No applications currently playing audio found.")
            return []
            
        apps = []
        for sink in sink_inputs:
            app_info = {
                'index': sink.index,
                'name': sink.name,
                'application': sink.proplist.get('application.name', ''),
                'binary': sink.proplist.get('application.process.binary', ''),
                'pid': sink.proplist.get('application.process.id', ''),
                'sink': sink.sink
            }
            apps.append(app_info)
            print(f"Found application: {app_info}")
            
        return apps

    def capture_application(self, sink_index):
        try:
            # 确保 sink_index 是整数
            sink_index = int(sink_index)
            
            # 获取所有 sink inputs
            sink_inputs = self.pulse.sink_input_list()
            target_sink_input = None
            
            # 查找目标 sink input
            for sink in sink_inputs:
                if sink.index == sink_index:
                    target_sink_input = sink
                    break
            
            if not target_sink_input:
                raise ValueError(f"No sink input found with index {sink_index}")
            
            print(f"\nTarget application details:")
            print(f"Index: {target_sink_input.index}")
            print(f"Name: {target_sink_input.name}")
            print(f"Application: {target_sink_input.proplist.get('application.name', '')}")
            
            # 获取当前的 sink
            original_sink = target_sink_input.sink
            print(f"Original sink: {original_sink}")
            
            # 创建一个虚拟 sink
            virtual_sink_name = "virtual_sink"
            virtual_sink_id = self.pulse.module_load("module-null-sink", f"sink_name={virtual_sink_name}")
            print(f"Created virtual sink with ID: {virtual_sink_id}")
            
            try:
                # 等待虚拟 sink 创建完成
                time.sleep(0.5)
                
                # 获取所有 sinks
                sinks = self.pulse.sink_list()
                virtual_sink = None
                for sink in sinks:
                    if sink.name == virtual_sink_name:
                        virtual_sink = sink
                        break
                
                if not virtual_sink:
                    raise ValueError("Could not find virtual sink")
                
                print(f"Moving sink input {target_sink_input.index} to virtual sink {virtual_sink.index}")
                
                # 将目标应用的音频重定向到虚拟 sink
                self.pulse.sink_input_move(target_sink_input.index, virtual_sink.index)
                
                # 获取虚拟 sink 的 monitor source
                monitor_source = virtual_sink.monitor_source_name
                print(f"Using monitor source: {monitor_source}")
                
                # 创建录制流
                self.stream = self.pulse.record_start(
                    source=monitor_source,
                    format='float32le',
                    rate=44100,
                    channels=2,
                    stream_name='audio-capture-stream',
                    buffer_attr=None,
                    flags=None,
                    volume=1.0
                )
                
                self.is_recording = True
                print("Started recording application audio...")
                
                # 开始录制
                while self.is_recording:
                    data = self.stream.read()
                    if data:
                        self.process_audio(np.frombuffer(data, dtype=np.float32))
                        
            finally:
                try:
                    # 将音频输出恢复到原始 sink
                    if target_sink_input and original_sink:
                        self.pulse.sink_input_move(target_sink_input.index, original_sink)
                except Exception as e:
                    print(f"Error restoring original sink: {e}")
                
                # 清理虚拟 sink
                if virtual_sink_id:
                    try:
                        self.pulse.module_unload(virtual_sink_id)
                    except Exception as e:
                        print(f"Error unloading virtual sink: {e}")
                    
        except Exception as e:
            print(f"Error capturing audio: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.stream:
                try:
                    self.stream.finish()
                except:
                    pass

    def stop_capture(self):
        self.is_recording = False
        print("\nStopping audio capture...")

    def process_audio(self, audio_data):
        # 处理音频数据
        # 这里可以添加你的音频处理逻辑
        print(f"Processing audio data: shape={audio_data.shape}, max={np.max(audio_data)}, min={np.min(audio_data)}")

    def cleanup(self):
        if self.pulse:
            self.pulse.close()