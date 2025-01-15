import win32com.client
import win32api
import win32gui
import win32process
import comtypes
from comtypes import CLSCTX_ALL
from ctypes import POINTER, cast
import numpy as np

# Windows Audio Session API
from comtypes.gen import MMDeviceAPI
from comtypes.gen import AudioClient

class WindowsAudioCapture:
    def __init__(self):
        self.is_recording = False
        self.device = None
        self.client = None
        self.capture = None

    def list_applications(self):
        # 获取音频会话管理器
        deviceEnumerator = comtypes.CoCreateInstance(
            MMDeviceAPI.MMDeviceEnumerator,
            clsctx=CLSCTX_ALL
        )
        
        # 获取默认音频端点
        device = deviceEnumerator.GetDefaultAudioEndpoint(0, 0)
        
        # 获取音频会话管理器
        sessionManager = device.Activate(
            MMDeviceAPI.IAudioSessionManager2._iid_,
            CLSCTX_ALL,
            None
        )
        
        # 获取会话枚举器
        sessionEnumerator = sessionManager.GetSessionEnumerator()
        
        apps = []
        for session in sessionEnumerator:
            try:
                process_id = session.GetProcessId()
                if process_id != 0:
                    handle = win32api.OpenProcess(0x0400, False, process_id)
                    exe_path = win32process.GetModuleFileNameEx(handle, 0)
                    app_info = {
                        'pid': process_id,
                        'name': exe_path.split('\\')[-1],
                        'path': exe_path
                    }
                    apps.append(app_info)
                    print(f"Found application: {app_info}")
            except Exception as e:
                print(f"Error getting session info: {e}")
                
        return apps

    def capture_application(self, pid):
        try:
            # 初始化音频捕获
            deviceEnumerator = comtypes.CoCreateInstance(
                MMDeviceAPI.MMDeviceEnumerator,
                clsctx=CLSCTX_ALL
            )
            
            # 获取默认音频设备
            self.device = deviceEnumerator.GetDefaultAudioEndpoint(0, 0)
            
            # 激活音频客户端
            self.client = self.device.Activate(
                AudioClient.IAudioClient._iid_,
                CLSCTX_ALL,
                None
            )
            
            # 设置音频格式
            self.client.Initialize(
                0x88000000,  # AUDCLNT_SHAREMODE_SHARED
                0x00000001,  # AUDCLNT_STREAMFLAGS_LOOPBACK
                0,
                0,
                self.client.GetMixFormat(),
                None
            )
            
            # 获取捕获客户端
            self.capture = self.client.GetService(
                AudioClient.IAudioCaptureClient._iid_
            )
            
            # 开始捕获
            self.client.Start()
            self.is_recording = True
            
            while self.is_recording:
                # 读取音频数据
                buffer = self.capture.GetBuffer()
                if buffer:
                    audio_data = np.frombuffer(buffer, dtype=np.float32)
                    self.process_audio(audio_data)
                    
        except Exception as e:
            print(f"Error capturing audio: {e}")
            
    def stop_capture(self):
        self.is_recording = False
        if self.client:
            self.client.Stop()
            
    def process_audio(self, audio_data):
        # 处理音频数据
        pass

    def cleanup(self):
        self.stop_capture()