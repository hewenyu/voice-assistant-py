import platform

class AudioCaptureFactory:
    @staticmethod
    def create_capturer():
        system = platform.system().lower()
        if system == 'windows':
            from .win_audio_capture import WindowsAudioCapture
            return WindowsAudioCapture()
        elif system == 'linux':
            from .linux_audio_capture import LinuxAudioCapture
            return LinuxAudioCapture()
        else:
            raise NotImplementedError(f"Platform {system} not supported")
