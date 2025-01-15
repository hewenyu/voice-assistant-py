import pulsectl
import numpy as np
import time

class LinuxAudioCapture:
    def __init__(self):
        self.pulse = pulsectl.Pulse('audio-capture')
        self.stream = None
        self.is_recording = False
        self.monitor_module = None
        self.loopback_module = None

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
            
            # 获取默认输出设备
            default_sink = self.pulse.server_info().default_sink_name
            
            # 创建一个 null sink 作为监听源
            monitor_name = "audio_monitor"
            self.monitor_module = self.pulse.module_load(
                "module-null-sink",
                f"sink_name={monitor_name}"
            )
            
            print(f"Created monitor sink with ID: {self.monitor_module}")
            
            # 创建一个 loopback 从目标应用到监听源
            self.loopback_module = self.pulse.module_load(
                "module-loopback",
                f"source={target_sink_input.sink}.monitor sink={monitor_name} latency_msec=1"
            )
            
            print(f"Created loopback with ID: {self.loopback_module}")
            
            try:
                # 等待监听模块创建完成
                time.sleep(0.5)
                
                # 获取监听源
                monitor_source = None
                for source in self.pulse.source_list():
                    if source.name == f"{monitor_name}.monitor":
                        monitor_source = source
                        break
                
                if not monitor_source:
                    raise ValueError("Could not find monitor source")
                
                print(f"Using monitor source: {monitor_source.name}")
                
                # 设置事件回调
                def audio_callback(ev):
                    if not self.is_recording:
                        raise pulsectl.PulseLoopStop
                    
                    # 检查事件类型，ev_t 是事件类型
                    if ev.t == pulsectl.PulseEventTypeEnum.new:
                        data = ev.data
                        if data:
                            self.process_audio(np.frombuffer(data, dtype=np.float32))
                
                # 设置事件监听
                self.is_recording = True
                print("Started recording application audio...")
                
                self.pulse.event_mask_set('all')
                self.pulse.event_callback_set(audio_callback)
                self.pulse.event_listen()
                        
            finally:
                self.cleanup()
        except Exception as e:
            print(f"Error capturing audio: {e}")
            self.cleanup()

    def stop_capture(self):
        """停止录音并清理资源"""
        print("Stopping audio capture...")
        self.is_recording = False
        # 停止事件循环
        self.pulse.event_listen_stop()
        # 等待事件循环完全停止
        time.sleep(0.5)
        self.cleanup()

    def cleanup(self):
        """清理资源"""
        if self.loopback_module:
            try:
                self.pulse.module_unload(self.loopback_module)
                print("Unloaded loopback module")
            except Exception as e:
                print(f"Error unloading loopback module: {e}")
            self.loopback_module = None

        if self.monitor_module:
            try:
                self.pulse.module_unload(self.monitor_module)
                print("Unloaded monitor module")
            except Exception as e:
                print(f"Error unloading monitor module: {e}")
            self.monitor_module = None

    def process_audio(self, audio_data):
        """处理音频数据"""
        # 这里可以添加你的音频处理逻辑
        pass