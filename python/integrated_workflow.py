"""
Integrated AI Workflow
=======================
Интеграция всех 4 проектов в единый рабочий процесс:
  1. AI Agent — принимает задачу
  2. Self-Healing Agent — генерирует код
  3. Document Agent — создаёт отчёт
  4. Flash Arbitrage — (опционально) выполняет торговую стратегию

Пример: Автоматическая генерация кода + отчёта + тестирование
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Импортируем все модули
try:
    from self_healing_agent import SelfHealingAgent
    from document_agent import DocumentAnalyzer, DocumentGenerator, AutoReportGenerator
    from agent import AIAgent
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь что все модули установлены:")
    print("  pip install openai python-docx")
    sys.exit(1)


class IntegratedWorkflow:
    """Интегрированный рабочий процесс."""
    
    def __init__(self):
        self.code_agent = SelfHealingAgent()
        self.doc_analyzer = DocumentAnalyzer()
        self.doc_generator = DocumentGenerator()
        self.auto_report = AutoReportGenerator()
        self.ai_agent = AIAgent()
        
        self.workspace = Path("integrated_workspace")
        self.workspace.mkdir(exist_ok=True)
        
        self.reports_dir = self.workspace / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        self.code_dir = self.workspace / "code"
        self.code_dir.mkdir(exist_ok=True)
    
    def workflow_1_code_and_report(self, task: str) -> Dict[str, Any]:
        """
        Workflow 1: Генерация кода + автоматический отчёт
        
        1. AI Agent анализирует задачу
        2. Self-Healing Agent генерирует и тестирует код
        3. Document Agent создаёт отчёт о результатах
        """
        print("\n" + "="*70)
        print("🔄 Workflow 1: Code + Report Generation")
        print("="*70)
        print(f"Задача: {task}\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Шаг 1: Генерация кода
        print("📝 Шаг 1: Генерация кода...")
        code_result = self.code_agent.execute_task(task)
        
        if not code_result.completed:
            print("❌ Не удалось сгенерировать код")
            return {"success": False, "error": "Code generation failed"}
        
        # Шаг 2: Анализ результатов
        print("\n📊 Шаг 2: Анализ результатов...")
        code_stats = {
            "files_created": len(code_result.files_created),
            "iterations": code_result.total_iterations,
            "healing_attempts": len(code_result.healing_attempts),
            "files": [f.path for f in code_result.files_created]
        }
        
        # Шаг 3: Создание отчёта
        print("\n📄 Шаг 3: Создание отчёта...")
        
        # Создаём шаблон отчёта
        template_path = self._create_report_template()
        
        # Данные для отчёта
        report_data = {
            "task_description": task,
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "files_created": str(code_stats["files_created"]),
            "iterations": str(code_stats["iterations"]),
            "healing_attempts": str(code_stats["healing_attempts"]),
            "status": "✅ Успешно" if code_result.completed else "❌ Не удалось",
            "files_list": "\n".join([f"  - {Path(f).name}" for f in code_stats["files"]]),
            "summary": self._generate_summary(code_result)
        }
        
        # Генерируем отчёт
        report_path = str(self.reports_dir / f"report_{timestamp}.docx")
        self.doc_generator.load_template(template_path)
        doc_result = self.doc_generator.generate_from_data(report_data, report_path)
        
        print(f"\n✅ Workflow завершён!")
        print(f"   Код: {self.code_dir}")
        print(f"   Отчёт: {report_path}")
        
        return {
            "success": True,
            "code_result": code_result,
            "report_path": report_path,
            "stats": code_stats
        }
    
    def workflow_2_ai_analysis_and_report(self, topic: str) -> Dict[str, Any]:
        """
        Workflow 2: AI анализ + отчёт
        
        1. AI Agent исследует тему
        2. Собирает информацию
        3. Document Agent создаёт аналитический отчёт
        """
        print("\n" + "="*70)
        print("🔄 Workflow 2: AI Analysis + Report")
        print("="*70)
        print(f"Тема: {topic}\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Шаг 1: AI анализ
        print("🤖 Шаг 1: AI анализ темы...")
        analysis_task = f"""
        Проведи исследование на тему: {topic}
        
        1. Найди ключевую информацию
        2. Проанализируй данные
        3. Сделай выводы
        4. Сохрани результаты в файл analysis_results.json
        """
        
        ai_result = self.ai_agent.run_task(analysis_task)
        
        if not ai_result.completed:
            print("❌ AI анализ не завершён")
            return {"success": False, "error": "AI analysis failed"}
        
        # Шаг 2: Чтение результатов
        print("\n📊 Шаг 2: Чтение результатов анализа...")
        analysis_file = self.workspace / "analysis_results.json"
        
        if analysis_file.exists():
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
        else:
            analysis_data = {"topic": topic, "findings": ai_result.final_answer}
        
        # Шаг 3: Создание отчёта
        print("\n📄 Шаг 3: Создание аналитического отчёта...")
        
        template_path = self._create_analysis_template()
        
        report_data = {
            "topic": topic,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "key_findings": json.dumps(analysis_data.get("findings", "Нет данных"), ensure_ascii=False),
            "conclusions": analysis_data.get("conclusions", "Выводы требуют дополнительной проверки"),
            "recommendations": analysis_data.get("recommendations", "Рекомендации будут добавлены позже")
        }
        
        report_path = str(self.reports_dir / f"analysis_{timestamp}.docx")
        self.doc_generator.load_template(template_path)
        doc_result = self.doc_generator.generate_from_data(report_data, report_path)
        
        print(f"\n✅ Workflow завершён!")
        print(f"   Отчёт: {report_path}")
        
        return {
            "success": True,
            "ai_result": ai_result,
            "report_path": report_path
        }
    
    def workflow_3_batch_reports(self, tasks: List[str]) -> Dict[str, Any]:
        """
        Workflow 3: Пакетная генерация отчётов
        
        1. Для каждой задачи генерируется код
        2. Для каждого результата создаётся отчёт
        3. Финальный сводный отчёт
        """
        print("\n" + "="*70)
        print("🔄 Workflow 3: Batch Report Generation")
        print("="*70)
        print(f"Задач: {len(tasks)}\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results = []
        
        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] {task}")
            
            # Генерируем код
            code_result = self.code_agent.execute_task(task)
            
            # Создаём отчёт
            template_path = self._create_report_template()
            
            report_data = {
                "task_description": task,
                "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "files_created": str(len(code_result.files_created)),
                "iterations": str(code_result.total_iterations),
                "healing_attempts": str(len(code_result.healing_attempts)),
                "status": "✅ Успешно" if code_result.completed else "❌ Не удалось",
                "files_list": "\n".join([f"  - {Path(f).name}" for f in code_result.files_created]),
                "summary": self._generate_summary(code_result)
            }
            
            report_path = str(self.reports_dir / f"report_{i}_{timestamp}.docx")
            self.doc_generator.load_template(template_path)
            doc_result = self.doc_generator.generate_from_data(report_data, report_path)
            
            results.append({
                "task": task,
                "code_completed": code_result.completed,
                "report_path": report_path
            })
        
        # Сводный отчёт
        print(f"\n📊 Создание сводного отчёта...")
        summary_template = self._create_summary_template()
        
        summary_data = {
            "total_tasks": str(len(tasks)),
            "successful": str(sum(1 for r in results if r["code_completed"])),
            "failed": str(sum(1 for r in results if not r["code_completed"])),
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tasks_list": "\n".join([f"{i+1}. {r['task']}" for i, r in enumerate(results)])
        }
        
        summary_path = str(self.reports_dir / f"summary_{timestamp}.docx")
        self.doc_generator.load_template(summary_template)
        self.doc_generator.generate_from_data(summary_data, summary_path)
        
        print(f"\n✅ Batch workflow завершён!")
        print(f"   Отчётов создано: {len(results)}")
        print(f"   Сводный отчёт: {summary_path}")
        
        return {
            "success": True,
            "results": results,
            "summary_path": summary_path
        }
    
    def _create_report_template(self) -> str:
        """Создаёт шаблон отчёта о генерации кода."""
        from docx import Document
        
        template_path = self.workspace / "code_report_template.docx"
        
        doc = Document()
        doc.add_heading('Отчёт о генерации кода', 0)
        
        doc.add_heading('Описание задачи', 1)
        doc.add_paragraph('{{task_description}}')
        
        doc.add_heading('Результаты', 1)
        doc.add_paragraph('Дата генерации: {{generation_date}}')
        doc.add_paragraph('Статус: {{status}}')
        doc.add_paragraph('Файлов создано: {{files_created}}')
        doc.add_paragraph('Итераций: {{iterations}}')
        doc.add_paragraph('Попыток исправления: {{healing_attempts}}')
        
        doc.add_heading('Созданные файлы', 1)
        doc.add_paragraph('{{files_list}}')
        
        doc.add_heading('Резюме', 1)
        doc.add_paragraph('{{summary}}')
        
        doc.save(template_path)
        return str(template_path)
    
    def _create_analysis_template(self) -> str:
        """Создаёт шаблон аналитического отчёта."""
        from docx import Document
        
        template_path = self.workspace / "analysis_template.docx"
        
        doc = Document()
        doc.add_heading('Аналитический отчёт', 0)
        
        doc.add_heading('Тема исследования', 1)
        doc.add_paragraph('{{topic}}')
        
        doc.add_heading('Дата анализа', 1)
        doc.add_paragraph('{{analysis_date}}')
        
        doc.add_heading('Ключевые findings', 1)
        doc.add_paragraph('{{key_findings}}')
        
        doc.add_heading('Выводы', 1)
        doc.add_paragraph('{{conclusions}}')
        
        doc.add_heading('Рекомендации', 1)
        doc.add_paragraph('{{recommendations}}')
        
        doc.save(template_path)
        return str(template_path)
    
    def _create_summary_template(self) -> str:
        """Создаёт шаблон сводного отчёта."""
        from docx import Document
        
        template_path = self.workspace / "summary_template.docx"
        
        doc = Document()
        doc.add_heading('Сводный отчёт', 0)
        
        doc.add_heading('Общая статистика', 1)
        doc.add_paragraph('Дата: {{generation_date}}')
        doc.add_paragraph('Всего задач: {{total_tasks}}')
        doc.add_paragraph('Успешных: {{successful}}')
        doc.add_paragraph('Неудачных: {{failed}}')
        
        doc.add_heading('Список задач', 1)
        doc.add_paragraph('{{tasks_list}}')
        
        doc.save(template_path)
        return str(template_path)
    
    def _generate_summary(self, code_result) -> str:
        """Генерирует текстовое резюме результатов."""
        if code_result.completed:
            return (
                f"Код успешно сгенерирован за {code_result.total_iterations} итераций. "
                f"Создано {len(code_result.files_created)} файл(ов). "
                f"Все файлы прошли тестирование."
            )
        else:
            return (
                f"Генерация кода не завершена. "
                f"Выполнено {code_result.total_iterations} итераций. "
                f"Попыток исправления: {len(code_result.healing_attempts)}. "
                f"Требуется ручная доработка."
            )


# ─── Main ────────────────────────────────────────────────────────

def main():
    """Главная функция."""
    print("\n" + "="*70)
    print("🔄 Integrated AI Workflow")
    print("="*70)
    
    workflow = IntegratedWorkflow()
    
    print("\nВыберите workflow:")
    print("  1. Code + Report (генерация кода + отчёт)")
    print("  2. AI Analysis + Report (AI анализ + отчёт)")
    print("  3. Batch Reports (пакетная генерация)")
    print("  4. Выход\n")
    
    choice = input("Ваш выбор: ").strip()
    
    if choice == "1":
        task = input("\n📝 Задача: ").strip()
        if task:
            result = workflow.workflow_1_code_and_report(task)
            if result["success"]:
                print(f"\n✅ Готово! Отчёт: {result['report_path']}")
    
    elif choice == "2":
        topic = input("\n🔍 Тема исследования: ").strip()
        if topic:
            result = workflow.workflow_2_ai_analysis_and_report(topic)
            if result["success"]:
                print(f"\n✅ Готово! Отчёт: {result['report_path']}")
    
    elif choice == "3":
        print("\n📦 Пакетная генерация")
        print("Введите задачи (по одной, пустая строка для завершения):")
        
        tasks = []
        while True:
            task = input(f"  Задача {len(tasks)+1}: ").strip()
            if not task:
                break
            tasks.append(task)
        
        if tasks:
            result = workflow.workflow_3_batch_reports(tasks)
            if result["success"]:
                print(f"\n✅ Готово! Сводный отчёт: {result['summary_path']}")
    
    else:
        print("👋 До свидания!")


if __name__ == "__main__":
    main()
