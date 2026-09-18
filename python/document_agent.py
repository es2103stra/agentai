"""
Document Analyzer & Generator
==============================
Анализ DOCX документов и генерация новых на основе шаблонов.

Возможности:
  • Извлечение текста, таблиц, изображений
  • Анализ структуры (заголовки, стили, форматирование)
  • Генерация нового документа с теми же стилями
  • Поддержка шаблонов с плейсхолдерами
  • Интеграция с GPT-4 для генерации контента

Запуск:
    python document_agent.py analyze report.docx
    python document_agent.py generate template.docx --data new_data.json
    python document_agent.py auto-report template.docx "Квартальный отчёт Q4 2024"
"""

import os
import sys
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    print("Установите python-docx: pip install python-docx")
    sys.exit(1)

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

OUTPUT_DIR = Path("generated_docs")
OUTPUT_DIR.mkdir(exist_ok=True)


# ─── Модели ──────────────────────────────────────────────────────

@dataclass
class DocumentStructure:
    """Структура документа."""
    title: str
    sections: List[Dict[str, Any]]
    styles_used: List[str]
    tables_count: int
    images_count: int
    total_paragraphs: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentTemplate:
    """Шаблон документа."""
    source_path: str
    structure: DocumentStructure
    placeholders: List[str]
    styles: Dict[str, Any]
    content_map: Dict[str, str]  # placeholder -> content


@dataclass
class GeneratedDocument:
    """Сгенерированный документ."""
    path: str
    template_used: str
    placeholders_filled: int
    generation_time: float
    word_count: int


# ─── Document Analyzer ───────────────────────────────────────────

class DocumentAnalyzer:
    """Анализатор DOCX документов."""
    
    def __init__(self):
        self.doc = None
        self.structure = None
    
    def analyze(self, file_path: str) -> DocumentStructure:
        """Анализирует документ и извлекает структуру."""
        print(f"📄 Анализирую: {file_path}")
        
        self.doc = Document(file_path)
        
        # Извлекаем заголовки и секции
        sections = []
        styles_used = set()
        placeholders = []
        
        current_section = None
        
        for para in self.doc.paragraphs:
            style_name = para.style.name if para.style else "Normal"
            styles_used.add(style_name)
            
            # Определяем тип параграфа
            if "Heading" in style_name:
                # Новый раздел
                if current_section:
                    sections.append(current_section)
                
                current_section = {
                    "type": "heading",
                    "level": int(style_name.replace("Heading ", "")) if style_name != "Heading" else 1,
                    "text": para.text,
                    "style": style_name,
                    "content": []
                }
            elif para.text.strip():
                # Обычный параграф
                text = para.text
                
                # Ищем плейсхолдеры {{placeholder}}
                found_placeholders = re.findall(r'\{\{(\w+)\}\}', text)
                placeholders.extend(found_placeholders)
                
                if current_section:
                    current_section["content"].append({
                        "type": "paragraph",
                        "text": text,
                        "style": style_name
                    })
        
        if current_section:
            sections.append(current_section)
        
        # Считаем таблицы
        tables_count = len(self.doc.tables)
        
        # Считаем изображения
        images_count = 0
        for rel in self.doc.part.rels.values():
            if "image" in rel.reltype:
                images_count += 1
        
        # Извлекаем заголовок (первый Heading 1 или первый параграф)
        title = ""
        for section in sections:
            if section["level"] == 1:
                title = section["text"]
                break
        
        if not title and self.doc.paragraphs:
            title = self.doc.paragraphs[0].text
        
        # Метаданные
        metadata = {
            "author": self.doc.core_properties.author,
            "created": str(self.doc.core_properties.created),
            "modified": str(self.doc.core_properties.modified),
        }
        
        self.structure = DocumentStructure(
            title=title,
            sections=sections,
            styles_used=list(styles_used),
            tables_count=tables_count,
            images_count=images_count,
            total_paragraphs=len(self.doc.paragraphs),
            metadata=metadata
        )
        
        print(f"✅ Структура извлечена:")
        print(f"   Заголовок: {title}")
        print(f"   Секций: {len(sections)}")
        print(f"   Таблиц: {tables_count}")
        print(f"   Изображений: {images_count}")
        print(f"   Плейсхолдеров: {len(placeholders)}")
        
        return self.structure
    
    def extract_placeholders(self) -> List[str]:
        """Извлекает все плейсхолдеры из документа."""
        placeholders = []
        
        for para in self.doc.paragraphs:
            found = re.findall(r'\{\{(\w+)\}\}', para.text)
            placeholders.extend(found)
        
        return list(set(placeholders))
    
    def extract_text_content(self) -> str:
        """Извлекает весь текстовый контент."""
        return "\n\n".join([para.text for para in self.doc.paragraphs if para.text.strip()])
    
    def extract_tables(self) -> List[List[List[str]]]:
        """Извлекает все таблицы."""
        tables = []
        
        for table in self.doc.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                table_data.append(row_data)
            tables.append(table_data)
        
        return tables
    
    def export_structure(self, output_path: str = None) -> Dict[str, Any]:
        """Экспортирует структуру в JSON."""
        if not self.structure:
            raise ValueError("Сначала проанализируйте документ")
        
        structure_dict = {
            "title": self.structure.title,
            "sections": self.structure.sections,
            "styles_used": self.structure.styles_used,
            "tables_count": self.structure.tables_count,
            "images_count": self.structure.images_count,
            "total_paragraphs": self.structure.total_paragraphs,
            "metadata": self.structure.metadata,
            "placeholders": self.extract_placeholders()
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(structure_dict, f, ensure_ascii=False, indent=2)
            print(f"✅ Структура сохранена: {output_path}")
        
        return structure_dict


# ─── Document Generator ──────────────────────────────────────────

class DocumentGenerator:
    """Генератор документов на основе шаблонов."""
    
    def __init__(self):
        self.template_doc = None
        self.analyzer = DocumentAnalyzer()
    
    def load_template(self, template_path: str):
        """Загружает шаблон документа."""
        print(f"📋 Загружаю шаблон: {template_path}")
        self.template_doc = Document(template_path)
        self.analyzer.analyze(template_path)
    
    def generate_from_data(self, data: Dict[str, Any], output_path: str) -> GeneratedDocument:
        """Генерирует документ из данных."""
        if not self.template_doc:
            raise ValueError("Сначала загрузите шаблон")
        
        start_time = datetime.now()
        
        # Создаём копию шаблона
        new_doc = Document(self.template_doc.element)
        
        placeholders_filled = 0
        word_count = 0
        
        # Заменяем плейсхолдеры
        for para in new_doc.paragraphs:
            original_text = para.text
            
            # Ищем плейсхолдеры
            for key, value in data.items():
                placeholder = f"{{{{{key}}}}}"
                if placeholder in para.text:
                    para.text = para.text.replace(placeholder, str(value))
                    placeholders_filled += 1
            
            word_count += len(para.text.split())
        
        # Сохраняем
        new_doc.save(output_path)
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        result = GeneratedDocument(
            path=output_path,
            template_used=self.template_doc.path if hasattr(self.template_doc, 'path') else "template",
            placeholders_filled=placeholders_filled,
            generation_time=generation_time,
            word_count=word_count
        )
        
        print(f"✅ Документ сгенерирован:")
        print(f"   Путь: {output_path}")
        print(f"   Плейсхолдеров заполнено: {placeholders_filled}")
        print(f"   Слов: {word_count}")
        print(f"   Время: {generation_time:.2f}s")
        
        return result
    
    def generate_with_ai(self, task: str, output_path: str) -> GeneratedDocument:
        """Генерирует документ с помощью GPT-4."""
        if not self.template_doc:
            raise ValueError("Сначала загрузите шаблон")
        
        print(f"🤖 Генерирую контент с GPT-4...")
        
        # Извлекаем структуру
        structure = self.analyzer.export_structure()
        placeholders = self.analyzer.extract_placeholders()
        
        # Запрос к GPT-4
        prompt = f"""Ты — эксперт по созданию документов. 

Задача: {task}

Структура шаблона:
{json.dumps(structure, ensure_ascii=False, indent=2)}

Плейсхолдеры для заполнения: {', '.join(placeholders)}

Сгенерируй содержимое для каждого плейсхолдера в формате JSON:
{{
  "placeholder_name": "содержимое",
  ...
}}

Правила:
1. Контент должен соответствовать структуре
2. Используй профессиональный стиль
3. Будь конкретным и детальным
4. Сохраняй форматирование"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Ты — эксперт по созданию документов."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        generated_data = json.loads(response.choices[0].message.content)
        
        print(f"✅ Контент сгенерирован для {len(generated_data)} плейсхолдеров")
        
        # Генерируем документ
        return self.generate_from_data(generated_data, output_path)


# ─── Auto Report Generator ───────────────────────────────────────

class AutoReportGenerator:
    """Автоматическая генерация отчётов."""
    
    def __init__(self):
        self.analyzer = DocumentAnalyzer()
        self.generator = DocumentGenerator()
    
    def generate_report(
        self, 
        template_path: str, 
        task: str, 
        output_path: str = None
    ) -> GeneratedDocument:
        """Генерирует отчёт автоматически."""
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(OUTPUT_DIR / f"report_{timestamp}.docx")
        
        print(f"\n{'='*70}")
        print(f"📊 Auto Report Generator")
        print(f"{'='*70}")
        print(f"Шаблон: {template_path}")
        print(f"Задача: {task}")
        print(f"Выход: {output_path}\n")
        
        # Загружаем шаблон
        self.generator.load_template(template_path)
        
        # Генерируем с AI
        result = self.generator.generate_with_ai(task, output_path)
        
        print(f"\n{'='*70}")
        print(f"✅ Отчёт успешно сгенерирован!")
        print(f"{'='*70}\n")
        
        return result
    
    def batch_generate(
        self,
        template_path: str,
        tasks: List[str]
    ) -> List[GeneratedDocument]:
        """Генерирует несколько отчётов пакетно."""
        results = []
        
        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] Генерирую: {task}")
            result = self.generate_report(template_path, task)
            results.append(result)
        
        return results


# ─── CLI ─────────────────────────────────────────────────────────

def main():
    """Главная функция."""
    if len(sys.argv) < 2:
        print("\nИспользование:")
        print("  python document_agent.py analyze <file.docx>")
        print("  python document_agent.py generate <template.docx> --data <data.json>")
        print("  python document_agent.py auto-report <template.docx> <task>")
        print()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        if len(sys.argv) < 3:
            print("Укажите файл: python document_agent.py analyze report.docx")
            sys.exit(1)
        
        file_path = sys.argv[2]
        analyzer = DocumentAnalyzer()
        structure = analyzer.analyze(file_path)
        
        # Экспортируем структуру
        output_json = file_path.replace('.docx', '_structure.json')
        analyzer.export_structure(output_json)
        
        # Показываем плейсхолдеры
        placeholders = analyzer.extract_placeholders()
        if placeholders:
            print(f"\n📝 Плейсхолдеры:")
            for p in placeholders:
                print(f"   - {{{{{p}}}}}")
    
    elif command == "generate":
        if len(sys.argv) < 5:
            print("Использование: python document_agent.py generate template.docx --data data.json")
            sys.exit(1)
        
        template_path = sys.argv[2]
        data_path = sys.argv[4]
        
        # Загружаем данные
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        generator = DocumentGenerator()
        generator.load_template(template_path)
        
        output_path = template_path.replace('.docx', '_generated.docx')
        result = generator.generate_from_data(data, output_path)
    
    elif command == "auto-report":
        if len(sys.argv) < 4:
            print("Использование: python document_agent.py auto-report template.docx 'Задача'")
            sys.exit(1)
        
        template_path = sys.argv[2]
        task = " ".join(sys.argv[3:])
        
        auto_gen = AutoReportGenerator()
        result = auto_gen.generate_report(template_path, task)
        
        print(f"\n📄 Документ создан: {result.path}")
    
    else:
        print(f"Неизвестная команда: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
