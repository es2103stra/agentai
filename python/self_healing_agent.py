"""
Self-Healing AI Agent
======================
Агент с автоматическим исправлением ошибок:
  • Генерирует файлы (код, конфиги, скрипты)
  • Запускает их для тестирования
  • При ошибке — анализирует и РЕДАКТИРУЕТ файл
  • Повторяет цикл до успеха
  • Работает в фоне (daemon mode)
  • Логирует все попытки и исправления

Запуск:
    python self_healing_agent.py "Создай Flask API с CRUD операциями"
    python self_healing_agent.py --daemon  # фоновый режим
"""

import os
import sys
import time
import json
import subprocess
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import threading
import signal

try:
    from openai import OpenAI
except ImportError:
    print("Установите openai: pip install openai")
    sys.exit(1)

# ─── Конфигурация ────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Установите OPENAI_API_KEY")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4-turbo-preview"

# Настройки
MAX_ITERATIONS = 10  # максимум попыток исправления
MAX_EDIT_ATTEMPTS = 5  # максимум редактирований одного файла
WORKSPACE_DIR = Path("workspace")
LOG_DIR = Path("logs")
WORKSPACE_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# ─── Модели ──────────────────────────────────────────────────────

@dataclass
class FileArtifact:
    """Сгенерированный файл."""
    path: str
    content: str
    language: str  # 'python', 'javascript', 'bash', etc.
    created_at: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)
    version: int = 1
    edit_history: List[Dict] = field(default_factory=list)
    
    def get_hash(self) -> str:
        """Хеш содержимого для отслеживания изменений."""
        return hashlib.md5(self.content.encode()).hexdigest()


@dataclass
class TestResult:
    """Результат тестирования файла."""
    file_path: str
    success: bool
    output: str
    error: str
    exit_code: int
    duration: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class HealingAttempt:
    """Попытка исправления ошибки."""
    iteration: int
    file_path: str
    error_type: str
    error_message: str
    fix_applied: str
    success: bool
    timestamp: float = field(default_factory=time.time)


@dataclass
class TaskResult:
    """Результат выполнения задачи."""
    task: str
    completed: bool
    files_created: List[FileArtifact]
    test_results: List[TestResult]
    healing_attempts: List[HealingAttempt]
    total_iterations: int
    final_status: str
    timestamp: float = field(default_factory=time.time)


# ─── File Generator ──────────────────────────────────────────────

class FileGenerator:
    """Генератор файлов с помощью GPT-4."""
    
    def __init__(self):
        self.system_prompt = """Ты — эксперт-программист. Твоя задача — создавать файлы кода.

Для каждого файла отвечай в формате JSON:
{
  "files": [
    {
      "path": "путь/к/файлу.py",
      "language": "python",
      "content": "содержимое файла",
      "description": "описание что делает файл"
    }
  ],
  "run_command": "команда для запуска (если нужно)",
  "test_command": "команда для тестирования (если нужно)"
}

Правила:
1. Код должен быть рабочим и протестированным
2. Добавляй комментарии и docstrings
3. Обрабатывай ошибки
4. Используй лучшие практики
5. Если нужен requirements.txt — создай его
6. Если нужен запуск — укажи команду"""

    def generate_files(self, task: str) -> Dict[str, Any]:
        """Генерирует файлы для задачи."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Задача: {task}\n\nСоздай необходимые файлы."}
        ]
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    
    def save_files(self, generation_result: Dict[str, Any]) -> List[FileArtifact]:
        """Сохраняет сгенерированные файлы."""
        files = []
        
        for file_data in generation_result.get("files", []):
            path = WORKSPACE_DIR / file_data["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Сохраняем файл
            with open(path, 'w', encoding='utf-8') as f:
                f.write(file_data["content"])
            
            # Создаём артефакт
            artifact = FileArtifact(
                path=str(path),
                content=file_data["content"],
                language=file_data.get("language", "text"),
            )
            files.append(artifact)
            
            print(f"✅ Создан: {path}")
        
        return files


# ─── Test Runner ─────────────────────────────────────────────────

class TestRunner:
    """Запуск и тестирование файлов."""
    
    @staticmethod
    def run_file(file_path: str, run_command: str = None) -> TestResult:
        """Запускает файл и возвращает результат."""
        start_time = time.time()
        
        # Определяем команду запуска
        if run_command:
            cmd = run_command
        else:
            ext = Path(file_path).suffix.lower()
            if ext == '.py':
                cmd = f"python {file_path}"
            elif ext == '.js':
                cmd = f"node {file_path}"
            elif ext == '.sh':
                cmd = f"bash {file_path}"
            else:
                return TestResult(
                    file_path=file_path,
                    success=False,
                    output="",
                    error=f"Unknown file type: {ext}",
                    exit_code=-1,
                    duration=0
                )
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=WORKSPACE_DIR
            )
            
            duration = time.time() - start_time
            
            return TestResult(
                file_path=file_path,
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode,
                duration=duration
            )
        
        except subprocess.TimeoutExpired:
            return TestResult(
                file_path=file_path,
                success=False,
                output="",
                error="Execution timed out (30s)",
                exit_code=-1,
                duration=30
            )
        except Exception as e:
            return TestResult(
                file_path=file_path,
                success=False,
                output="",
                error=str(e),
                exit_code=-1,
                duration=time.time() - start_time
            )
    
    @staticmethod
    def analyze_error(test_result: TestResult) -> Dict[str, str]:
        """Анализирует ошибку и определяет тип."""
        error = test_result.error
        
        error_types = {
            "SyntaxError": "syntax",
            "ImportError": "import",
            "ModuleNotFoundError": "import",
            "NameError": "name",
            "TypeError": "type",
            "ValueError": "value",
            "AttributeError": "attribute",
            "FileNotFoundError": "file",
            "PermissionError": "permission",
            "IndentationError": "indentation",
        }
        
        error_type = "unknown"
        for key, value in error_types.items():
            if key in error:
                error_type = value
                break
        
        return {
            "type": error_type,
            "message": error[:500],  # ограничиваем размер
            "stdout": test_result.output[:500]
        }


# ─── Code Healer ─────────────────────────────────────────────────

class CodeHealer:
    """Автоматическое исправление ошибок в коде."""
    
    def __init__(self):
        self.system_prompt = """Ты — эксперт по отладке кода. Твоя задача — исправить ошибки в коде.

Тебе даны:
1. Содержимое файла с ошибкой
2. Текст ошибки
3. Тип ошибки

Исправь код так, чтобы ошибка исчезла.

Отвечай в формате JSON:
{
  "analysis": "анализ ошибки",
  "fix_description": "описание исправления",
  "fixed_content": "полное исправленное содержимое файла"
}

Правила:
1. Исправляй ТОЛЬКО ошибку, не меняй остальной код
2. Сохраняй структуру и стиль оригинала
3. Добавляй комментарии если нужно
4. Убедись что исправление действительно решает проблему"""

    def heal_file(
        self, 
        file_artifact: FileArtifact, 
        error_info: Dict[str, str]
    ) -> Tuple[FileArtifact, str]:
        """Исправляет файл и возвращает новую версию."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user", 
                "content": f"""Файл: {file_artifact.path}
Язык: {file_artifact.language}

Содержимое:
```{file_artifact.language}
{file_artifact.content}
```

Ошибка ({error_info['type']}):
{error_info['message']}

stdout:
{error_info.get('stdout', '')}

Исправь код."""
            }
        ]
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Создаём новую версию файла
        fixed_content = result["fixed_content"]
        
        # Обновляем артефакт
        file_artifact.content = fixed_content
        file_artifact.last_modified = time.time()
        file_artifact.version += 1
        
        # Добавляем в историю редактирования
        file_artifact.edit_history.append({
            "version": file_artifact.version,
            "timestamp": time.time(),
            "analysis": result.get("analysis", ""),
            "fix": result.get("fix_description", ""),
            "error_type": error_info["type"]
        })
        
        # Сохраняем исправленный файл
        with open(file_artifact.path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"🔧 Исправлено (v{file_artifact.version}): {file_artifact.path}")
        print(f"   Анализ: {result.get('analysis', '')}")
        print(f"   Исправление: {result.get('fix_description', '')}")
        
        return file_artifact, result.get("fix_description", "")


# ─── Self-Healing Agent ──────────────────────────────────────────

class SelfHealingAgent:
    """Агент с автоматическим исправлением ошибок."""
    
    def __init__(self):
        self.generator = FileGenerator()
        self.runner = TestRunner()
        self.healer = CodeHealer()
        self.task_log: List[TaskResult] = []
    
    def execute_task(self, task: str) -> TaskResult:
        """Выполняет задачу с самоисцелением."""
        print(f"\n{'='*70}")
        print(f"🚀 Задача: {task}")
        print(f"{'='*70}\n")
        
        files_created = []
        test_results = []
        healing_attempts = []
        iteration = 0
        
        # 1. Генерация файлов
        print("📝 Генерирую файлы...")
        generation_result = self.generator.generate_files(task)
        files = self.generator.save_files(generation_result)
        files_created.extend(files)
        
        run_command = generation_result.get("run_command")
        test_command = generation_result.get("test_command")
        
        print(f"\n📦 Создано {len(files)} файл(ов)")
        
        # 2. Цикл тестирования и исправления
        while iteration < MAX_ITERATIONS:
            iteration += 1
            print(f"\n--- Итерация {iteration}/{MAX_ITERATIONS} ---\n")
            
            all_success = True
            
            # Тестируем каждый файл
            for file_artifact in files_created:
                print(f"🧪 Тестирую: {file_artifact.path}")
                
                test_result = self.runner.run_file(
                    file_artifact.path, 
                    run_command if file_artifact == files_created[0] else None
                )
                test_results.append(test_result)
                
                if test_result.success:
                    print(f"✅ Успешно ({test_result.duration:.2f}s)")
                    if test_result.output:
                        print(f"   Output: {test_result.output[:200]}")
                else:
                    all_success = False
                    print(f"❌ Ошибка (exit code: {test_result.exit_code})")
                    print(f"   Error: {test_result.error[:200]}")
                    
                    # Проверяем лимит редактирований
                    if file_artifact.version > MAX_EDIT_ATTEMPTS:
                        print(f"⚠️  Достигнут лимит редактирований для {file_artifact.path}")
                        continue
                    
                    # Анализируем ошибку
                    error_info = self.runner.analyze_error(test_result)
                    print(f"🔍 Тип ошибки: {error_info['type']}")
                    
                    # Исправляем
                    print(f"🔧 Исправляю...")
                    fixed_file, fix_desc = self.healer.heal_file(file_artifact, error_info)
                    
                    # Логируем попытку
                    healing_attempts.append(HealingAttempt(
                        iteration=iteration,
                        file_path=file_artifact.path,
                        error_type=error_info["type"],
                        error_message=error_info["message"],
                        fix_applied=fix_desc,
                        success=False  # проверим в следующей итерации
                    ))
            
            # Если всё успешно — завершаем
            if all_success:
                print(f"\n✅ Все файлы работают!")
                break
            
            # Пауза перед следующей итерацией
            time.sleep(1)
        
        # Финальный статус
        completed = all_success
        final_status = "SUCCESS" if completed else "FAILED"
        
        print(f"\n{'='*70}")
        print(f"📊 Результат: {final_status}")
        print(f"   Итераций: {iteration}")
        print(f"   Файлов создано: {len(files_created)}")
        print(f"   Попыток исправления: {len(healing_attempts)}")
        print(f"{'='*70}\n")
        
        # Создаём результат
        result = TaskResult(
            task=task,
            completed=completed,
            files_created=files_created,
            test_results=test_results,
            healing_attempts=healing_attempts,
            total_iterations=iteration,
            final_status=final_status
        )
        
        # Логируем
        self._log_task(result)
        self.task_log.append(result)
        
        return result
    
    def _log_task(self, result: TaskResult):
        """Логирует результат задачи."""
        log_entry = {
            "timestamp": result.timestamp,
            "task": result.task,
            "completed": result.completed,
            "iterations": result.total_iterations,
            "files_count": len(result.files_created),
            "healing_attempts": len(result.healing_attempts),
            "final_status": result.final_status,
            "files": [
                {
                    "path": f.path,
                    "version": f.version,
                    "edits": len(f.edit_history)
                }
                for f in result.files_created
            ]
        }
        
        log_file = LOG_DIR / "tasks.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        # Логируем детали редактирований
        if result.healing_attempts:
            details_file = LOG_DIR / f"task_{int(result.timestamp)}.json"
            with open(details_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "task": result.task,
                    "files": [
                        {
                            "path": file.path,
                            "version": file.version,
                            "edit_history": file.edit_history
                        }
                        for file in result.files_created
                    ]
                }, f, ensure_ascii=False, indent=2)
    
    def run_daemon(self):
        """Запуск в фоновом режиме."""
        print("\n" + "="*70)
        print("🤖 Self-Healing Agent — Daemon Mode")
        print("="*70)
        print("\nОжидание задач...")
        print("Для выхода: Ctrl+C\n")
        
        # Обработчик сигналов
        def signal_handler(sig, frame):
            print("\n\n⚠️  Остановка агента...")
            self._save_daemon_state()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Основной цикл
        while True:
            try:
                # Проверяем очередь задач
                task = self._get_next_task()
                
                if task:
                    print(f"\n📥 Новая задача: {task}")
                    result = self.execute_task(task)
                    
                    # Уведомление
                    self._notify_completion(result)
                
                # Пауза
                time.sleep(5)
            
            except Exception as e:
                print(f"\n❌ Ошибка в daemon: {e}")
                time.sleep(10)
    
    def _get_next_task(self) -> Optional[str]:
        """Получает следующую задачу из очереди."""
        queue_file = WORKSPACE_DIR / "task_queue.txt"
        
        if not queue_file.exists():
            return None
        
        with open(queue_file, 'r', encoding='utf-8') as f:
            tasks = f.readlines()
        
        if not tasks:
            return None
        
        # Берём первую задачу
        task = tasks[0].strip()
        
        # Удаляем из очереди
        with open(queue_file, 'w', encoding='utf-8') as f:
            f.writelines(tasks[1:])
        
        return task
    
    def _save_daemon_state(self):
        """Сохраняет состояние агента."""
        state = {
            "tasks_completed": len(self.task_log),
            "last_task": self.task_log[-1].task if self.task_log else None,
            "timestamp": time.time()
        }
        
        state_file = LOG_DIR / "daemon_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    
    def _notify_completion(self, result: TaskResult):
        """Уведомляет о завершении задачи."""
        status = "✅" if result.completed else "❌"
        message = f"{status} Задача: {result.task[:50]}... | Статус: {result.final_status}"
        
        print(f"\n🔔 {message}\n")
        
        # Можно добавить email, telegram, slack уведомления


# ─── Main ────────────────────────────────────────────────────────

def main():
    """Главная функция."""
    print("\n" + "="*70)
    print("🤖 Self-Healing AI Agent")
    print("="*70)
    
    agent = SelfHealingAgent()
    
    # Режим работы
    if len(sys.argv) > 1:
        if sys.argv[1] == "--daemon":
            # Фоновый режим
            agent.run_daemon()
        else:
            # Задача из аргументов
            task = " ".join(sys.argv[1:])
            result = agent.execute_task(task)
            
            if not result.completed:
                sys.exit(1)
    else:
        # Интерактивный режим
        print("\nРежимы:")
        print("  1. Одна задача")
        print("  2. Daemon mode (фон)")
        print("  3. Выход\n")
        
        choice = input("Выберите: ").strip()
        
        if choice == "1":
            task = input("\n📝 Задача: ").strip()
            if task:
                agent.execute_task(task)
        elif choice == "2":
            agent.run_daemon()
        else:
            print("👋 До свидания!")


if __name__ == "__main__":
    main()
