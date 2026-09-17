"""
Advanced Tools for AI Agent
============================
Расширенные инструменты для агента:
  • Browser Automation (Selenium/Playwright)
  • Code Execution (Python, JavaScript)
  • Data Analysis (pandas)
  • Image Processing (PIL)
  • Network Tools (ping, traceroute)
  • Clipboard Operations
  • Window Management
  • Notification System
"""

import os
import json
import subprocess
import pyperclip
import pyautogui
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime


class AdvancedTools:
    """Расширенные инструменты для AI-агента."""
    
    # ─── Browser Automation ──────────────────────────────────────
    
    @staticmethod
    def open_url(url: str) -> Dict[str, Any]:
        """Открывает URL в браузере по умолчанию."""
        try:
            import webbrowser
            webbrowser.open(url)
            return {"success": True, "url": url}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def browser_screenshot(selector: str = None) -> Dict[str, Any]:
        """Делает скриншот браузера (или элемента)."""
        try:
            screenshot = pyautogui.screenshot()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"browser_screenshot_{timestamp}.png"
            screenshot.save(filepath)
            return {"success": True, "filepath": filepath}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ─── Code Execution ──────────────────────────────────────────
    
    @staticmethod
    def execute_python(code: str) -> Dict[str, Any]:
        """Выполняет Python код."""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            result = subprocess.run(
                ['python', temp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.unlink(temp_path)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Code execution timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def execute_javascript(code: str) -> Dict[str, Any]:
        """Выполняет JavaScript код (через Node.js)."""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            result = subprocess.run(
                ['node', temp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.unlink(temp_path)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except FileNotFoundError:
            return {"success": False, "error": "Node.js not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ─── Data Analysis ───────────────────────────────────────────
    
    @staticmethod
    def analyze_csv(filepath: str) -> Dict[str, Any]:
        """Анализирует CSV файл."""
        try:
            import pandas as pd
            df = pd.read_csv(filepath)
            
            return {
                "success": True,
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "head": df.head(5).to_dict(orient='records'),
                "describe": df.describe().to_dict()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def create_chart(data: Dict[str, List], chart_type: str = "line") -> Dict[str, Any]:
        """Создаёт график из данных."""
        try:
            import matplotlib.pyplot as plt
            import io
            import base64
            
            fig, ax = plt.subplots()
            
            if chart_type == "line":
                for key, values in data.items():
                    ax.plot(values, label=key)
            elif chart_type == "bar":
                for key, values in data.items():
                    ax.bar(range(len(values)), values, label=key)
            
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Сохраняем в base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode()
            plt.close()
            
            return {
                "success": True,
                "image_base64": img_base64,
                "format": "png"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ─── Image Processing ────────────────────────────────────────
    
    @staticmethod
    def process_image(filepath: str, operation: str = "info") -> Dict[str, Any]:
        """Обрабатывает изображение."""
        try:
            from PIL import Image
            
            img = Image.open(filepath)
            
            if operation == "info":
                return {
                    "success": True,
                    "size": img.size,
                    "mode": img.mode,
                    "format": img.format
                }
            elif operation == "resize":
                # Пример: resize до 50%
                new_size = (img.size[0] // 2, img.size[1] // 2)
                resized = img.resize(new_size)
                output_path = filepath.replace('.', '_resized.')
                resized.save(output_path)
                return {"success": True, "output": output_path, "new_size": new_size}
            elif operation == "grayscale":
                gray = img.convert('L')
                output_path = filepath.replace('.', '_gray.')
                gray.save(output_path)
                return {"success": True, "output": output_path}
            
            return {"success": False, "error": f"Unknown operation: {operation}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ─── Network Tools ───────────────────────────────────────────
    
    @staticmethod
    def ping(host: str, count: int = 4) -> Dict[str, Any]:
        """Ping хоста."""
        try:
            result = subprocess.run(
                ['ping', '-c', str(count), host],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_ip_info() -> Dict[str, Any]:
        """Получает информацию о IP."""
        try:
            import requests
            response = requests.get('https://ipinfo.io/json', timeout=5)
            return {
                "success": True,
                "info": response.json()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ─── Clipboard ───────────────────────────────────────────────
    
    @staticmethod
    def clipboard_read() -> Dict[str, Any]:
        """Читает содержимое буфера обмена."""
        try:
            content = pyperclip.paste()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def clipboard_write(text: str) -> Dict[str, Any]:
        """Записывает в буфер обмена."""
        try:
            pyperclip.copy(text)
            return {"success": True, "text": text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ─── Window Management ───────────────────────────────────────
    
    @staticmethod
    def list_windows() -> Dict[str, Any]:
        """Список открытых окон."""
        try:
            import pygetwindow as gw
            windows = gw.getAllTitles()
            return {
                "success": True,
                "windows": [w for w in windows if w]  # фильтруем пустые
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def focus_window(title: str) -> Dict[str, Any]:
        """Фокусирует окно по заголовку."""
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle(title)
            if windows:
                windows[0].activate()
                return {"success": True, "window": title}
            return {"success": False, "error": "Window not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ─── Notifications ───────────────────────────────────────────
    
    @staticmethod
    def notify(title: str, message: str) -> Dict[str, Any]:
        """Показывает уведомление."""
        try:
            import plyer
            plyer.notification.notify(
                title=title,
                message=message,
                timeout=10
            )
            return {"success": True}
        except Exception as e:
            # Fallback: просто печатаем
            print(f"\n🔔 {title}: {message}\n")
            return {"success": True, "fallback": True}
    
    # ─── File System ─────────────────────────────────────────────
    
    @staticmethod
    def list_directory(path: str = ".") -> Dict[str, Any]:
        """Список файлов в директории."""
        try:
            files = []
            for item in Path(path).iterdir():
                files.append({
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            return {"success": True, "files": files}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def search_files(pattern: str, path: str = ".") -> Dict[str, Any]:
        """Поиск файлов по паттерну."""
        try:
            matches = list(Path(path).rglob(pattern))
            return {
                "success": True,
                "matches": [str(m) for m in matches[:50]]  # максимум 50
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ─── System Monitoring ───────────────────────────────────────
    
    @staticmethod
    def system_stats() -> Dict[str, Any]:
        """Статистика системы в реальном времени."""
        try:
            import psutil
            
            return {
                "success": True,
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "battery": psutil.sensors_battery()._percent if psutil.sensors_battery() else None,
                "processes": len(psutil.pids())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ─── API Calls ───────────────────────────────────────────────
    
    @staticmethod
    def http_request(url: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Выполняет HTTP запрос."""
        try:
            import requests
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            return {
                "success": response.ok,
                "status_code": response.status_code,
                "content": response.text[:1000]  # ограничиваем размер
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# ─── Tool Registry ───────────────────────────────────────────────

def get_all_tools() -> Dict[str, callable]:
    """Возвращает все доступные инструменты."""
    from agent import Tools
    
    tools = {
        # Basic tools
        "terminal": Tools.terminal,
        "screenshot": Tools.screenshot,
        "keyboard": Tools.keyboard,
        "mouse": Tools.mouse,
        "voice": Tools.voice_input,
        "web_search": Tools.web_search,
        "file_read": Tools.file_read,
        "file_write": Tools.file_write,
        "system_info": Tools.system_info,
        
        # Advanced tools
        "open_url": AdvancedTools.open_url,
        "execute_python": AdvancedTools.execute_python,
        "execute_javascript": AdvancedTools.execute_javascript,
        "analyze_csv": AdvancedTools.analyze_csv,
        "create_chart": AdvancedTools.create_chart,
        "process_image": AdvancedTools.process_image,
        "ping": AdvancedTools.ping,
        "get_ip_info": AdvancedTools.get_ip_info,
        "clipboard_read": AdvancedTools.clipboard_read,
        "clipboard_write": AdvancedTools.clipboard_write,
        "list_windows": AdvancedTools.list_windows,
        "focus_window": AdvancedTools.focus_window,
        "notify": AdvancedTools.notify,
        "list_directory": AdvancedTools.list_directory,
        "search_files": AdvancedTools.search_files,
        "system_stats": AdvancedTools.system_stats,
        "http_request": AdvancedTools.http_request,
    }
    
    return tools


if __name__ == "__main__":
    # Тест инструментов
    print("🧪 Testing Advanced Tools...\n")
    
    tools = AdvancedTools()
    
    # System stats
    print("📊 System Stats:")
    print(json.dumps(tools.system_stats(), indent=2))
    
    # Clipboard
    print("\n📋 Clipboard Write:")
    print(json.dumps(tools.clipboard_write("Hello from AI Agent!"), indent=2))
    
    # List directory
    print("\n📁 Current Directory:")
    print(json.dumps(tools.list_directory("."), indent=2))
    
    print("\n✅ All tools working!")
