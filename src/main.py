from audio.audio_capture_factory import AudioCaptureFactory
import threading
import time


def main():
    # 创建平台特定的捕获器
    capturer = AudioCaptureFactory.create_capturer()
    
    try:
        while True:
            # 列出应用程序
            apps = capturer.list_applications()
            
            if not apps:
                print("\nNo applications playing audio found. Waiting 5 seconds before trying again...")
                print("Press Ctrl+C to exit")
                time.sleep(5)
                continue
            
            # 选择第一个应用程序进行捕获
            app = apps[0]
            print(f"\nCapturing audio from: {app['name']}")
            
            # 在新线程中启动捕获
            capture_thread = threading.Thread(
                target=capturer.capture_application,
                args=(app['index'],)
            )
            capture_thread.start()
            
            # 等待用户输入来停止
            input("\nPress Enter to stop capturing...")
            
            # 停止捕获
            capturer.stop_capture()
            capture_thread.join()
            break
            
    finally:
        capturer.cleanup()

if __name__ == "__main__":
    main()