# 🍅 Pomodoro Timer  番茄计时器

## 简介 / Overview  
A minimalist Pomodoro Timer built with Python & Tkinter to boost focus. Features a fixed window, time logging, and a clickable copy icon.  
简洁的番茄计时器，使用 Python 和 Tkinter 打造，提升专注力。支持固定窗口、时间记录和可点击复制图标。

## 特性 / Features  
- ⏰ **Pomodoro**: 25min work, 5min break (customizable)  
  **番茄工作法**：25分钟工作，5分钟休息（可调）  
- 🖼️ **Fixed UI**: 400x400, draggable, non-resizable  
  **固定界面**：400x400，可拖动，不可缩放  
- 📝 **Time Log**: Record timer values, scrollable  
  **时间记录**：记录计时，滚动查看  
- 📋 **Copy Icon**: One-click copy of all records  
  **复制图标**：一键复制所有记录  

## 安装 / Installation  
1. Clone or download:  
   克隆或下载：  
   ```bash
   git clone https://github.com/BlairCode/PomodoroTimer.git
   ```
2. Install dependencies:  
   安装依赖：  
   ```bash
   pip install Pillow pyperclip
   ```
3. Add `copy.png` (32x32) to the project folder.  
   将 `copy.png`（32x32）放入项目文件夹。

## 使用 / Usage  
Run `python pomodoro_timer.py` and:  
运行 `python pomodoro_timer.py`，然后：  
- **Start/Pause**: Toggle timer with "Start".  
  **开始/暂停**：点击“Start”切换计时。  
- **Record**: Save time with "Record".  
  **记录**：点击“Record”保存时间。  
- **Copy**: Click the top-right icon to copy logs.  
  **复制**：点击右上图标复制记录。  
- **Reset**: Restart with "Reset".  
  **重置**：点击“Reset”重启。

## 依赖 / Dependencies  
- Python 3.9+  
- Tkinter  
- Pillow  
- pyperclip  
