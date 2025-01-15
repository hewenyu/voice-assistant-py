from audio.audio_capture_factory import AudioCaptureFactory
import threading


def main():
    # 创建平台特定的捕获器
    capturer = AudioCaptureFactory.create_capturer()
    
    try:
        # 列出应用程序
        apps = capturer.list_applications()
        
        if apps:
            # 选择第一个应用程序进行捕获
            app = apps[0]
            print(f"Capturing audio from: {app['name']}")
            
            # 在新线程中启动捕获
            capture_thread = threading.Thread(
                target=capturer.capture_application,
                args=(app['pid'] if 'pid' in app else app['index'],)
            )
            capture_thread.start()
            
            # 等待用户输入来停止
            input("Press Enter to stop capturing...")
            
            # 停止捕获
            capturer.stop_capture()
            capture_thread.join()
            
    finally:
        capturer.cleanup()

if __name__ == "__main__":
    main()