import sys
import os
import json
import threading
import asyncio

# 添加错误处理以便更好地诊断问题
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
except ImportError:
    print("错误: 无法导入tkinter库，这是Python标准库的一部分，请确保您的Python安装正确")
    sys.exit(1)

try:
    import pygame
except ImportError:
    print("错误: 无法导入pygame库，请使用pip install pygame安装")
    sys.exit(1)

try:
    import edge_tts
except ImportError:
    print("错误: 无法导入edge-tts库，请使用pip install edge-tts安装")
    sys.exit(1)

try:
    import win32com.client
    from comtypes.client import CreateObject
except ImportError:
    print("错误: 无法导入win32com或comtypes库，请使用pip install pywin32 comtypes安装")
    sys.exit(1)

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文字转语音程序")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 初始化状态变量
        self.status_var = tk.StringVar()
        self.status_var.set("正在初始化...")
        
        # 初始化pygame用于音频播放
        try:
            pygame.init()
            pygame.mixer.init()
            self.status_var.set("音频系统初始化成功")
        except Exception as e:
            print(f"初始化pygame失败: {e}")
            self.status_var.set("警告: 音频系统初始化失败")
        
        # 创建TTS服务商和语音选项
        self.tts_providers = {
            "Edge TTS": self.use_edge_tts,
            "Microsoft SAPI5": self.use_microsoft_sapi5
        }
        
        # 扫描系统音频设备
        self.audio_devices = self.get_audio_devices()
        
        # 创建UI界面
        self.create_widgets()
        
        # 更新音频设备列表
        self.update_audio_device_list()
        
        # 加载配置
        self.load_config()
        
        self.status_var.set("就绪")
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建上部控制区域
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        
        # TTS服务商选择
        ttk.Label(control_frame, text="TTS服务商:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.tts_provider_var = tk.StringVar()
        self.tts_provider_combo = ttk.Combobox(control_frame, textvariable=self.tts_provider_var, state="readonly")
        self.tts_provider_combo['values'] = list(self.tts_providers.keys())
        self.tts_provider_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.tts_provider_combo.current(0)
        self.tts_provider_combo.bind("<<ComboboxSelected>>", self.on_provider_change)
        
        # 语音选择
        ttk.Label(control_frame, text="语音选择:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(control_frame, textvariable=self.voice_var, state="readonly", width=30)
        self.voice_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 音频设备选择
        ttk.Label(control_frame, text="音频输出设备:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.audio_device_var = tk.StringVar()
        self.audio_device_combo = ttk.Combobox(control_frame, textvariable=self.audio_device_var, state="readonly", width=30)
        self.audio_device_combo['values'] = list(self.audio_devices.keys())
        self.audio_device_combo.grid(row=1, column=1, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        if len(self.audio_devices) > 0:
            self.audio_device_combo.current(0)
        
        # 刷新设备按钮
        refresh_btn = ttk.Button(control_frame, text="刷新设备", command=self.refresh_devices)
        refresh_btn.grid(row=1, column=4, padx=5, pady=5)
        
        # 创建文本输入区域
        text_frame = ttk.LabelFrame(main_frame, text="文本输入", padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.text_input = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=40, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 发送按钮
        self.send_btn = ttk.Button(button_frame, text="转换为语音", command=self.convert_to_speech)
        self.send_btn.pack(side=tk.RIGHT, padx=5)
        
        # 停止按钮
        self.stop_btn = ttk.Button(button_frame, text="停止", command=self.stop_speech)
        self.stop_btn.pack(side=tk.RIGHT, padx=5)
        
        # 状态栏 - 使用已在__init__中初始化的status_var
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 初始化语音列表
        self.update_voice_list()
    
    def on_provider_change(self, event=None):
        self.update_voice_list()
    
    def update_voice_list(self):
        provider = self.tts_provider_var.get()
        voices = []
        
        if provider == "Edge TTS":
            try:
                # 获取Edge TTS可用的语音列表
                voices = ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "zh-CN-YunjianNeural", "zh-CN-XiaoyiNeural", "zh-CN-YunyangNeural", "zh-CN-XiaochenNeural", "zh-CN-XiaohanNeural", "zh-CN-XiaomengNeural", "zh-CN-XiaomoNeural", "zh-CN-XiaoqiuNeural", "zh-CN-XiaoruiNeural", "zh-CN-XiaoshuangNeural", "zh-CN-XiaoxuanNeural", "zh-CN-XiaoyanNeural", "zh-CN-XiaoyouNeural", "zh-CN-XiaozhenNeural"]
            except Exception as e:
                print(f"获取Edge TTS语音失败: {e}")
                voices = ["无法获取Edge TTS语音"]
        elif provider == "Microsoft SAPI5":
            try:
                sapi = CreateObject("SAPI.SpVoice")
                voices = [voice.GetDescription() for voice in sapi.GetVoices()]
            except Exception as e:
                print(f"获取Microsoft SAPI5语音失败: {e}")
                voices = ["无法获取SAPI5语音"]
        
        self.voice_combo['values'] = voices
        if voices:
            self.voice_combo.current(0)
    
    def get_audio_devices(self):
        """扫描系统音频输出设备"""
        devices = {"默认设备": "default"}
        
        try:
            # 尝试使用win32com获取音频设备
            try:
                # 使用SAPI获取音频设备
                sapi = win32com.client.Dispatch("SAPI.SpVoice")
                audio_outputs = sapi.GetAudioOutputs()
                
                for i in range(audio_outputs.Count):
                    device_desc = audio_outputs.Item(i).GetDescription()
                    devices[device_desc] = i
                    
                self.status_var.set(f"已找到 {audio_outputs.Count} 个音频设备")
                
            except Exception as e:
                print(f"通过SAPI获取音频设备失败: {e}")
                # 备用方法：使用WMI获取音频设备
                try:
                    strComputer = "."
                    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
                    objSWbemServices = objWMIService.ConnectServer(strComputer, "root\\cimv2")
                    colItems = objSWbemServices.ExecQuery("Select * from Win32_SoundDevice")
                    
                    device_count = 0
                    for i, objItem in enumerate(colItems):
                        if objItem.Status == "OK":
                            devices[f"{objItem.Name}"] = f"device_{i}"
                            device_count += 1
                    
                    self.status_var.set(f"已找到 {device_count} 个音频设备")
                except Exception as e:
                    print(f"通过WMI获取音频设备失败: {e}")
                    self.status_var.set("无法获取音频设备列表，将使用默认设备")
        except Exception as e:
            print(f"获取音频设备时出现错误: {e}")
            self.status_var.set("获取音频设备失败，将使用默认设备")
        
        return devices
    
    def update_audio_device_list(self):
        """更新音频设备下拉列表"""
        if hasattr(self, 'audio_device_combo'):
            current_selection = self.audio_device_var.get() if hasattr(self, 'audio_device_var') else ""
            
            # 更新下拉列表
            self.audio_device_combo['values'] = list(self.audio_devices.keys())
            
            # 尝试保持之前的选择
            if current_selection and current_selection in self.audio_devices:
                self.audio_device_var.set(current_selection)
            elif len(self.audio_devices) > 0:
                self.audio_device_combo.current(0)
    
    def refresh_devices(self):
        """刷新音频设备列表"""
        self.status_var.set("正在扫描音频设备...")
        self.root.update_idletasks()  # 立即更新UI
        
        # 重新扫描设备
        self.audio_devices = self.get_audio_devices()
        self.update_audio_device_list()
        
        self.status_var.set(f"已刷新音频设备，找到 {len(self.audio_devices)} 个设备")
    
    def use_system_tts(self, text, voice_name):
        """使用系统内置TTS引擎"""
        self.engine.stop()
        
        # 设置语音
        voices = self.engine.getProperty('voices')
        for i, voice in enumerate(voices):
            if voice.name == voice_name:
                self.engine.setProperty('voice', voice.id)
                break
        
        # 设置音频设备
        # 由于pyttsx3不直接支持选择输出设备，我们使用SAPI5接口来设置音频设备
        device_name = self.audio_device_var.get()
        if device_name != "默认设备":
            try:
                # 使用SAPI5接口设置音频设备
                sapi = CreateObject("SAPI.SpVoice")
                audio_outputs = sapi.GetAudioOutputs()
                
                # 查找匹配的音频设备
                for i in range(audio_outputs.Count):
                    if device_name in audio_outputs.Item(i).GetDescription():
                        # 设置SAPI5的音频输出设备
                        sapi.AudioOutput = audio_outputs.Item(i)
                        
                        # 使用SAPI5播放，而不是pyttsx3
                        def speak_with_sapi():
                            try:
                                # 设置与pyttsx3相同的语音
                                voices_sapi = sapi.GetVoices()
                                for j in range(voices_sapi.Count):
                                    if voice_name in voices_sapi.Item(j).GetDescription():
                                        sapi.Voice = voices_sapi.Item(j)
                                        break
                                
                                sapi.Speak(text)
                                self.status_var.set("语音播放完成")
                            except Exception as e:
                                self.status_var.set(f"语音播放失败: {e}")
                        
                        threading.Thread(target=speak_with_sapi).start()
                        return  # 使用SAPI5播放后直接返回
            except Exception as e:
                print(f"设置音频设备失败，将使用默认设备: {e}")
        
        # 如果没有指定特定设备或设置设备失败，则使用pyttsx3默认方式播放
        def speak():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                self.status_var.set("语音播放完成")
            except Exception as e:
                self.status_var.set(f"语音播放失败: {e}")
        
        threading.Thread(target=speak).start()
    
    def use_microsoft_sapi5(self, text, voice_name):
        """使用Microsoft SAPI5引擎"""
        try:
            sapi = CreateObject("SAPI.SpVoice")
            
            # 设置语音
            voices = sapi.GetVoices()
            for i in range(voices.Count):
                if voices.Item(i).GetDescription() == voice_name:
                    sapi.Voice = voices.Item(i)
                    break
            
            # 设置音频设备
            device_name = self.audio_device_var.get()
            if device_name != "默认设备":
                try:
                    audio_outputs = sapi.GetAudioOutputs()
                    for i in range(audio_outputs.Count):
                        if device_name in audio_outputs.Item(i).GetDescription():
                            sapi.AudioOutput = audio_outputs.Item(i)
                            break
                except Exception as e:
                    print(f"设置音频设备失败: {e}")
            
            # 转换文本为语音
            def speak():
                try:
                    sapi.Speak(text)
                    self.status_var.set("语音播放完成")
                except Exception as e:
                    self.status_var.set(f"语音播放失败: {e}")
            
            threading.Thread(target=speak).start()
        
        except Exception as e:
            self.status_var.set(f"SAPI5初始化失败: {e}")
    
    def use_edge_tts(self, text, voice_name):
        """使用Edge TTS引擎"""
        try:
            def speak():
                try:
                    communicate = edge_tts.Communicate(text, voice_name)
                    # 创建异步函数来保存音频
                    async def save_audio():
                        await communicate.save("temp_edge_tts.mp3")
                    
                    # 运行异步函数
                    asyncio.run(save_audio())
                    
                    # 使用pygame播放生成的音频文件
                    pygame.mixer.music.load("temp_edge_tts.mp3")
                    pygame.mixer.music.play()
                    
                    # 等待播放完成
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    
                    self.status_var.set("语音播放完成")
                except Exception as e:
                    self.status_var.set(f"Edge TTS语音播放失败: {e}")
                finally:
                    # 删除临时文件
                    try:
                        os.remove("temp_edge_tts.mp3")
                    except:
                        pass
            
            threading.Thread(target=speak).start()
        except Exception as e:
            self.status_var.set(f"Edge TTS初始化失败: {e}")
    
    def convert_to_speech(self):
        """将文本转换为语音"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            self.status_var.set("请输入要转换的文本")
            return
        
        provider = self.tts_provider_var.get()
        voice_name = self.voice_var.get()
        
        self.status_var.set(f"正在使用 {provider} 转换文本为语音...")
        self.send_btn.config(state=tk.DISABLED)
        
        # 调用相应的TTS服务
        if provider in self.tts_providers:
            self.tts_providers[provider](text, voice_name)
        else:
            self.status_var.set(f"未知的TTS服务商: {provider}")
        
        self.send_btn.config(state=tk.NORMAL)
    
    def stop_speech(self):
        """停止语音播放"""
        provider = self.tts_provider_var.get()
        
        if provider == "系统内置TTS":
            self.engine.stop()
        elif provider == "Microsoft SAPI5":
            try:
                sapi = CreateObject("SAPI.SpVoice")
                sapi.Speak("", 3)  # 3 = SVSFPurgeBeforeSpeak
            except Exception as e:
                print(f"停止SAPI5语音失败: {e}")
        
        self.status_var.set("已停止语音播放")
    
    def save_config(self):
        """保存配置"""
        config = {
            "tts_provider": self.tts_provider_var.get(),
            "voice": self.voice_var.get(),
            "audio_device": self.audio_device_var.get()
        }
        
        try:
            with open("tts_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists("tts_config.json"):
                with open("tts_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                if "tts_provider" in config and config["tts_provider"] in self.tts_providers:
                    self.tts_provider_var.set(config["tts_provider"])
                    self.update_voice_list()
                
                if "voice" in config:
                    voices = self.voice_combo["values"]
                    if config["voice"] in voices:
                        self.voice_var.set(config["voice"])
                
                if "audio_device" in config and config["audio_device"] in self.audio_devices:
                    self.audio_device_var.set(config["audio_device"])
        except Exception as e:
            print(f"加载配置失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    
    # 在关闭窗口时保存配置
    def on_closing():
        app.save_config()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()