from flask import Flask, render_template, request, jsonify
from text_to_speech_web import TTSApp
import os
import asyncio
from functools import partial

# 确保templates目录存在
os.makedirs('templates', exist_ok=True)

app = Flask(__name__)
tts_app = TTSApp()

@app.route('/')
def index():
    # 获取TTS服务商列表和语音列表
    tts_providers = list(tts_app.tts_providers.keys())
    voices = tts_app.get_voice_list()
    # 获取音频设备列表
    audio_devices = tts_app.get_audio_devices()
    return render_template('index.html', 
                         tts_providers=tts_providers,
                         voices=voices,
                         audio_devices=audio_devices)

@app.route('/tts', methods=['POST'])
def tts_endpoint():
    try:
        data = request.get_json()
        text = data.get('text', '')
        provider = data.get('provider', '')
        voice_name = data.get('voice', '')
        device = data.get('device', '')
        
        if not text:
            return jsonify({'error': '请输入要转换的文本'}), 400
            
        # 设置音频设备
        tts_app.set_audio_device(device)
        
        # 调用TTS转换
        if provider in tts_app.tts_providers:
            if provider == "Edge TTS":
                # 创建新的事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # 运行异步函数
                success = loop.run_until_complete(tts_app.tts_providers[provider](text, voice_name))
                loop.close()
            else:
                success = tts_app.tts_providers[provider](text, voice_name)
                
            if success:
                return jsonify({'status': 'success', 'message': '转换完成'})
            else:
                return jsonify({'error': '转换失败'}), 500
        else:
            return jsonify({'error': f'未知的TTS服务商: {provider}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1145)