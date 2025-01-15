import platform

class AudioCaptureFactory:
    @staticmethod
    def create_capturer():
        system = platform.system().lower()
        if system == 'windows':
            from audio.win_audio_capture import WindowsAudioCapture
            return WindowsAudioCapture()
        elif system == 'linux':
            from audio.linux_audio_capture import LinuxAudioCapture
            return LinuxAudioCapture()
        else:
            raise NotImplementedError(f"Platform {system} not supported")
