import platform

class AudioCaptureFactory:
    @staticmethod
    def create_capturer():
        system = platform.system().lower()
        if system == 'windows':
            return WindowsAudioCapture()
        elif system == 'linux':
            return LinuxAudioCapture()
        else:
            raise NotImplementedError(f"Platform {system} not supported")
