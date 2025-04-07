import sys
import os
import json
import asyncio
from pythonosc import udp_client
import pygame
import edge_tts
import win32com.client
from comtypes.client import CreateObject

class TTSApp:
    def __init__(self):
        # 初始化VRChat OSC客户端
        try:
            self.osc_client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
            print("VRChat OSC客户端初始化成功")
        except Exception as e:
            print(f"VRChat OSC客户端初始化失败: {e}")
        
        # 初始化pygame用于音频播放
        try:
            pygame.init()
            pygame.mixer.init()
            print("音频系统初始化成功")
        except Exception as e:
            print(f"初始化pygame失败: {e}")
        
        # 创建TTS服务商和语音选项
        self.tts_providers = {
            "Edge TTS": self.use_edge_tts,
            "Microsoft SAPI5": self.use_microsoft_sapi5
        }
        
        # 扫描系统音频设备
        self.audio_devices = self.get_audio_devices()
        self.current_device = "default"
    
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
                    
                print(f"已找到 {audio_outputs.Count} 个音频设备")
                
            except Exception as e:
                print(f"通过SAPI获取音频设备失败: {e}")
                
        except Exception as e:
            print(f"获取音频设备失败: {e}")
        
        return devices
    
    def get_voice_list(self):
        """获取当前TTS服务商支持的语音列表"""
        voices = [
            # 女声
            "zh-CN-XiaoxiaoNeural",  # Female, News/Novel, Warm
            "zh-CN-XiaoyiNeural",    # Female, Cartoon/Novel, Lively
            "zh-CN-liaoning-XiaobeiNeural",  # Female, Dialect, Humorous
            "zh-CN-shaanxi-XiaoniNeural",   # Female, Dialect, Bright
            
            # 男声
            "zh-CN-YunjianNeural",   # Male, Sports/Novel, Passion
            "zh-CN-YunxiNeural",     # Male, Novel, Lively/Sunshine
            "zh-CN-YunxiaNeural",    # Male, Cartoon/Novel, Cute
            "zh-CN-YunyangNeural"    # Male, News, Professional/Reliable
        ]
        return voices
    
    def set_audio_device(self, device):
        """设置音频输出设备"""
        self.current_device = device
    
    async def use_edge_tts(self, text, voice_name):
        """使用Edge TTS服务转换文本"""
        temp_file = None
        try:
            # 发送文本到VRChat OSC
            try:
                self.osc_client.send_message("/chatbox/input", [text, True])
                print("已发送文本到VRChat OSC")
            except Exception as e:
                print(f"发送OSC消息失败: {e}")
            
            # 生成临时文件名
            import uuid
            temp_file = f"temp_edge_tts_{uuid.uuid4().hex}.mp3"
            
            # 确保临时文件不存在
            if os.path.exists(temp_file):
                try:
                    pygame.mixer.music.unload()
                except:
                    pass
                try:
                    os.remove(temp_file)
                except Exception as e:
                    print(f"删除已存在的临时文件失败: {e}")
                    return False
            
            # 使用edge-tts转换文本为语音
            communicate = edge_tts.Communicate(text, voice_name)
            await communicate.save(temp_file)
            
            # 设置音频设备
            if self.current_device != "default" and hasattr(pygame.mixer, 'get_init') and pygame.mixer.get_init():
                try:
                    pygame.mixer.quit()
                    pygame.mixer.init(devicename=self.current_device)
                except Exception as e:
                    print(f"设置音频设备失败: {e}")
                    # 如果设置失败，重新初始化默认设备
                    pygame.mixer.init()
            
            try:
                # 播放转换后的语音
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                
                # 等待播放完成
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                
                # 确保音频已卸载
                pygame.mixer.music.unload()
                
                # 清理临时文件
                try:
                    os.remove(temp_file)
                except Exception as e:
                    print(f"清理临时文件失败: {e}")
                    # 即使清理失败也继续执行
                
                return True
            except Exception as e:
                print(f"播放音频失败: {e}")
                # 发生错误时也尝试清理资源
                try:
                    pygame.mixer.music.unload()
                except:
                    pass
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
                return False
            
        except Exception as e:
            print(f"Edge TTS转换失败: {e}")
            return False
            
        finally:
            # 清理所有临时文件
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                for file in os.listdir(current_dir):
                    if file.startswith('temp_edge_tts_') and file.endswith('.mp3'):
                        file_path = os.path.join(current_dir, file)
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                print(f"已清理临时文件: {file}")
                        except Exception as e:
                            print(f"清理临时文件 {file} 失败: {e}")
            except Exception as e:
                print(f"扫描清理临时文件失败: {e}")
    
    def use_microsoft_sapi5(self, text, voice_name):
        """使用Microsoft SAPI5服务转换文本"""
        try:
            # 发送文本到VRChat OSC
            try:
                self.osc_client.send_message("/chatbox/input", [text, True])
                print("已发送文本到VRChat OSC")
            except Exception as e:
                print(f"发送OSC消息失败: {e}")
            
            sapi = CreateObject("SAPI.SpVoice")
            
            # 设置语音
            voices = sapi.GetVoices()
            for i in range(voices.Count):
                if voices.Item(i).GetDescription() == voice_name:
                    sapi.Voice = voices.Item(i)
                    break
            
            # 设置音频输出设备
            if self.current_device != "default":
                audio_outputs = sapi.GetAudioOutputs()
                sapi.AudioOutput = audio_outputs.Item(self.current_device)
            
            # 转换并播放
            sapi.Speak(text)
            return True
            
        except Exception as e:
            print(f"Microsoft SAPI5转换失败: {e}")
            return False