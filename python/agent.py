"""
AI Agent — Autonomous Computer Use Agent
==========================================
Автономный AI-агент с:
  • Computer Use (управление мышью/клавиатурой)
  • Terminal Execution (выполнение команд)
  • Voice Input (распознавание речи через Whisper)
  • Loop Execution (цикл пока задача не выполнена)
  • OpenAI GPT-4 для принятия решений
  • Расширенные инструменты (web, files, system)

Запуск:
    pip install -r requirements.txt
    export OPENAI_API_KEY="your-key-here"
    python agent.py
"""

import os
import sys
import time
import json
import subprocess
import pyautogui
import speech_recognition as sr
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import requests
from pathlib import Path

# OpenAI
try:
    from openai import OpenAI
except ImportError:
    print("Установите openai: pip install openai")
    sys.exit(1)

# ─── Конфигурация ────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Установите OPENAI_API_KEY:")
    print("  export OPENAI_API_KEY='your-key-here'")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4-turbo-preview"  # или gpt-4-vision-preview для computer use

# Настройки агента
MAX_ITERATIONS = 50  # максимум итераций в цикле
SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)
LOG_FILE = Path("agent_log.jsonl")

# ─── Модели ──────────────────────────────────────────────────────

@dataclass
class Action:
    """Действие агента."""
    type: str  # 'terminal', 'keyboard', 'mouse', 'screenshot', 'voice', 'web', 'file'
    command: str
    description: str
    timestamp: float = field(default_factory=time.time)
    result: Optional[str] = None
    success: Optional[bool] = None


@dataclass
class TaskResult:
    """Результат выполнения задачи."""
    task: str
    completed: bool
    iterations: int
    actions: List[Action]
    final_answer: str
    timestamp: float = field(default_factory=time.time)


# ─── Tools (Инструменты агента) ──────────────────────────────────

class Tools:
    """Набор инструментов для агента."""
    
    @staticmethod
    def terminal(command: str, timeout: int = 30) -> Dict[str, Any]:
        """Выполняет команду в терминале."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def screenshot() -> str:
        """Делает скриншот экрана."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = SCREENSHOT_DIR / f"screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(str(filepath))
        return str(filepath)
    
    @staticmethod
    def keyboard(type_text: str = None, hotkey: List[str] = None, press_key: str = None):
        """Управление клавиатурой."""
        if type_text:
            pyautogui.typewrite(type_text, interval=0.05)
            return {"success": True, "action": f"Typed: {type_text}"}
        elif hotkey:
            pyautogui.hotkey(*hotkey)
            return {"success": True, "action": f"Pressed: {'+'.join(hotkey)}"}
        elif press_key:
            pyautogui.press(press_key)
            return {"success": True, "action": f"Pressed: {press_key}"}
        return {"success": False, "error": "No action specified"}
    
    @staticmethod
    def mouse(click: bool = False, move_to: tuple = None, scroll: int = 0):
        """Управление мышью."""
        if move_to:
            pyautogui.moveTo(move_to[0], move_to[1])
        if click:
            pyautogui.click()
        if scroll:
            pyautogui.scroll(scroll)
        
        current_pos = pyautogui.position()
        return {
            "success": True,
            "position": {"x": current_pos.x, "y": current_pos.y},
            "actions": {
                "moved": move_to is not None,
                "clicked": click,
                "scrolled": scroll
            }
        }
    
    @staticmethod
    def voice_input(timeout: int = 10) -> Dict[str, Any]:
        """Распознавание речи через микрофон."""
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                print("🎤 Слушаю...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=timeout)
                
            # Используем Whisper API
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio.get_wav_data())
                temp_path = f.name
            
            with open(temp_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            os.unlink(temp_path)
            return {"success": True, "text": transcript.text}
        except sr.WaitTimeoutError:
            return {"success": False, "error": "No speech detected"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def web_search(query: str) -> Dict[str, Any]:
        """Поиск в интернете (через DuckDuckGo)."""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def file_read(filepath: str) -> Dict[str, Any]:
        """Чтение файла."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def file_write(filepath: str, content: str) -> Dict[str, Any]:
        """Запись в файл."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "filepath": filepath}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def system_info() -> Dict[str, Any]:
        """Информация о системе."""
        import platform
        import psutil
        
        return {
            "success": True,
            "info": {
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                "memory_available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
                "disk_usage": f"{psutil.disk_usage('/').percent}%"
            }
        }


# ─── AI Agent ────────────────────────────────────────────────────

class AIAgent:
    """Автономный AI-агент с computer use."""
    
    def __init__(self):
        self.tools = Tools()
        self.conversation_history: List[Dict] = []
        self.actions_log: List[Action] = []
        
        # Системный промпт
        self.system_prompt = """Ты — автономный AI-агент с возможностями computer use.
Ты можешь:
1. Выполнять команды в терминале (tool: terminal)
2. Управлять клавиатурой (tool: keyboard)
3. Управлять мышью (tool: mouse)
4. Делать скриншоты (tool: screenshot)
5. Распознавать речь (tool: voice)
6. Искать в интернете (tool: web_search)
7. Читать/писать файлы (tool: file_read, file_write)
8. Получать информацию о системе (tool: system_info)

Ты работаешь в цикле:
1. Анализируешь задачу
2. Выбираешь действие
3. Выполняешь действие
4. Проверяешь результат
5. Повторяешь пока задача не выполнена

Для каждого действия отвечай в формате JSON:
{
  "thought": "Твои рассуждения",
  "action": {
    "tool": "название инструмента",
    "parameters": {параметры инструмента}
  },
  "task_completed": false/true,
  "final_answer": "ответ если задача выполнена"
}

Будь точным и эффективным. Проверяй результаты каждого действия."""

    def think_and_act(self, task: str) -> Dict[str, Any]:
        """Принимает решение и выбирает действие."""
        
        # Формируем сообщение для GPT
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Задача: {task}"}
        ]
        
        # Добавляем историю действий
        if self.actions_log:
            history = "\n".join([
                f"- {a.type}: {a.command} → {'✓' if a.success else '✗'}"
                for a in self.actions_log[-10:]  # последние 10 действий
            ])
            messages.append({
                "role": "user",
                "content": f"История действий:\n{history}\n\nПродолжай выполнение задачи."
            })
        
        # Запрос к GPT-4
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        decision = json.loads(response.choices[0].message.content)
        return decision
    
    def execute_action(self, action: Dict[str, Any]) -> Action:
        """Выполняет выбранное действие."""
        tool_name = action.get("tool")
        params = action.get("parameters", {})
        
        action_obj = Action(
            type=tool_name,
            command=str(params),
            description=f"Executing {tool_name}"
        )
        
        try:
            # Вызываем соответствующий инструмент
            if tool_name == "terminal":
                result = self.tools.terminal(**params)
            elif tool_name == "screenshot":
                filepath = self.tools.screenshot()
                result = {"success": True, "filepath": filepath}
            elif tool_name == "keyboard":
                result = self.tools.keyboard(**params)
            elif tool_name == "mouse":
                result = self.tools.mouse(**params)
            elif tool_name == "voice":
                result = self.tools.voice_input(**params)
            elif tool_name == "web_search":
                result = self.tools.web_search(**params)
            elif tool_name == "file_read":
                result = self.tools.file_read(**params)
            elif tool_name == "file_write":
                result = self.tools.file_write(**params)
            elif tool_name == "system_info":
                result = self.tools.system_info()
            else:
                result = {"success": False, "error": f"Unknown tool: {tool_name}"}
            
            action_obj.result = json.dumps(result, ensure_ascii=False, indent=2)
            action_obj.success = result.get("success", False)
            
        except Exception as e:
            action_obj.result = str(e)
            action_obj.success = False
        
        return action_obj
    
    def run_task(self, task: str) -> TaskResult:
        """Выполняет задачу в цикле."""
        print(f"\n{'='*60}")
        print(f"🚀 Задача: {task}")
        print(f"{'='*60}\n")
        
        actions = []
        iteration = 0
        
        while iteration < MAX_ITERATIONS:
            iteration += 1
            print(f"\n--- Итерация {iteration}/{MAX_ITERATIONS} ---\n")
            
            # 1. Думаем
            print("🧠 Думаю...")
            decision = self.think_and_act(task)
            
            thought = decision.get("thought", "")
            print(f"💭 {thought}\n")
            
            # 2. Проверяем завершение
            if decision.get("task_completed"):
                final_answer = decision.get("final_answer", "Задача выполнена")
                print(f"\n✅ Задача выполнена!")
                print(f"📝 Ответ: {final_answer}\n")
                
                return TaskResult(
                    task=task,
                    completed=True,
                    iterations=iteration,
                    actions=actions,
                    final_answer=final_answer
                )
            
            # 3. Выполняем действие
            action_data = decision.get("action", {})
            if not action_data:
                print("⚠️  Нет действия, завершаю цикл")
                break
            
            print(f"⚡ Выполняю: {action_data.get('tool')}")
            action_obj = self.execute_action(action_data)
            actions.append(action_obj)
            self.actions_log.append(action_obj)
            
            # 4. Показываем результат
            status = "✓" if action_obj.success else "✗"
            print(f"{status} Результат:")
            print(action_obj.result[:500] + "..." if len(action_obj.result) > 500 else action_obj.result)
            
            # 5. Пауза
            time.sleep(1)
        
        # Превышен лимит итераций
        print(f"\n⚠️  Достигнут лимит итераций ({MAX_ITERATIONS})")
        return TaskResult(
            task=task,
            completed=False,
            iterations=iteration,
            actions=actions,
            final_answer="Не удалось выполнить задачу за отведённое количество итераций"
        )
    
    def interactive_mode(self):
        """Интерактивный режим с голосовым вводом."""
        print("\n" + "="*60)
        print("🤖 AI Agent — Interactive Mode")
        print("="*60)
        print("\nКоманды:")
        print("  • Введите задачу текстом")
        print("  • 'voice' — голосовой ввод")
        print("  • 'quit' — выход")
        print()
        
        while True:
            try:
                # Ввод задачи
                user_input = input("\n📝 Задача: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 До свидания!")
                    break
                
                if user_input.lower() == 'voice':
                    print("\n🎤 Говорите...")
                    voice_result = self.tools.voice_input()
                    if voice_result["success"]:
                        user_input = voice_result["text"]
                        print(f"🗣️  Распознано: {user_input}")
                    else:
                        print(f"❌ Ошибка: {voice_result['error']}")
                        continue
                
                if not user_input:
                    continue
                
                # Выполняем задачу
                result = self.run_task(user_input)
                
                # Логируем
                self._log_result(result)
                
                # Сбрасываем историю для новой задачи
                self.actions_log = []
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Прервано пользователем")
                break
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
    
    def _log_result(self, result: TaskResult):
        """Логирует результат в файл."""
        log_entry = {
            "timestamp": result.timestamp,
            "task": result.task,
            "completed": result.completed,
            "iterations": result.iterations,
            "actions_count": len(result.actions),
            "final_answer": result.final_answer
        }
        
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


# ─── Main ────────────────────────────────────────────────────────

def main():
    """Главная функция."""
    print("\n" + "="*60)
    print("🤖 AI Agent — Autonomous Computer Use")
    print("="*60)
    print(f"\nМодель: {MODEL}")
    print(f"Максимум итераций: {MAX_ITERATIONS}")
    print(f"Лог файл: {LOG_FILE}")
    print()
    
    # Проверяем зависимости
    try:
        import psutil
    except ImportError:
        print("⚠️  Установите psutil: pip install psutil")
        return
    
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        print("⚠️  Установите duckduckgo-search: pip install duckduckgo-search")
    
    # Создаём агента
    agent = AIAgent()
    
    # Режим работы
    if len(sys.argv) > 1:
        # Задача из аргументов
        task = " ".join(sys.argv[1:])
        result = agent.run_task(task)
        agent._log_result(result)
    else:
        # Интерактивный режим
        agent.interactive_mode()


if __name__ == "__main__":
    main()
