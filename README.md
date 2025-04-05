# 文字转语音程序

这是一个基于Python的文字转语音(TTS)程序，可在Windows系统上运行。程序允许用户输入文本，选择TTS服务商和语音，并将文本转换为语音通过选定的音频输出设备播放。同时支持将文本同步发送到VRChat聊天框。

## 功能特点

- 单行文本输入界面，支持按回车键快速转换
- 历史记录框显示已转换的文本
- 支持多种TTS服务商（Microsoft SAPI5、Edge TTS）
- 自动扫描并列出系统上的音频输出设备
- 可选择不同的语音进行播放
- 保存用户配置，下次启动时自动加载
- 支持Edge TTS引擎，提供更自然的语音合成
- 支持VRChat OSC功能，可将文本同步发送到聊天框

## 安装说明

1. 确保您的系统已安装Python 3.6或更高版本
2. 安装所需依赖包：

```
pip install -r requirements.txt
```

注意：tkinter通常随Python一起安装，如果缺少，请参考Python官方文档安装。

## 使用方法

1. 运行程序：

```
python text_to_speech.py
```

2. 在文本输入框中输入要转换的文字，按回车键或点击「转换为语音」按钮
3. 从下拉菜单中选择TTS服务商和语音
4. 选择音频输出设备
5. 文本会自动转换为语音，并同步发送到VRChat聊天框（需要VRChat处于运行状态）

## 系统要求

- Windows 7/8/10/11
- Python 3.6+
- 至少一个可用的音频输出设备
- VRChat（如需使用OSC功能）

## 依赖安装

安装所需依赖：
```
pip install -r requirements.txt
```

requirements.txt包含：
- pygame
- pywin32
- comtypes
- edge-tts
- python-osc

## 故障排除

- 如果无法检测到音频设备，请点击「刷新设备」按钮
- 如果使用Microsoft SAPI5时出现问题，请确保Windows系统中已安装相应的语音包
- 如果播放时没有声音，请检查系统音量和选择的音频设备是否正确
- 如果VRChat OSC功能无法使用，请确保VRChat已启动并允许OSC连接