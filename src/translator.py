import polib
import time
import re
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# Стабильность определения языка
DetectorFactory.seed = 0

class POTask:
    def __init__(self, file_path, target_lang, log_callback, progress_callback, stop_event):
        self.file_path = file_path
        self.target_lang = target_lang
        self.log = log_callback
        self.update_progress = progress_callback
        self.stop_event = stop_event

    def protect_placeholders(self, text):
        """Заменяет технические вставки на метки [[0]], [[1]] и т.д."""
        placeholders = re.findall(r"(\{[^}]+\}|%\([^)]+\)s|%s|%d|%f)", text)
        temp_text = text
        for i, p in enumerate(placeholders):
            # Добавляем пробелы вокруг метки, чтобы переводчик не 'слил' её с текстом
            temp_text = temp_text.replace(p, f" [[{i}]] ")
        return temp_text, placeholders

    def restore_placeholders(self, text, placeholders):
        """Возвращает оригинальные вставки на место меток."""
        final_text = text
        for i, p in enumerate(placeholders):
            # Проверяем оба варианта (с пробелами и без), так как Google может менять пунктуацию
            final_text = final_text.replace(f"[[{i}]]", p).replace(f"[[ {i} ]]", p)
        return final_text.strip()

    def _should_translate(self, entry):
        if not entry.msgstr.strip():
            return True
        try:
            detected_lang = detect(entry.msgstr)
            if detected_lang != self.target_lang:
                return True 
        except:
            return True
        return False

    def run(self, smart_mode=True):
        try:
            po = polib.pofile(self.file_path)
            translator = GoogleTranslator(source='auto', target=self.target_lang)
            
            all_entries = [e for e in po if e.msgid and not e.obsolete]
            total = len(all_entries)
            
            self.log(f"🔎 Scanning {total} entries...")
            translated_count = 0

            for i, entry in enumerate(all_entries):
                # Проверка нажатия кнопки STOP
                if self.stop_event.is_set():
                    self.log("🛑 Process stopped by user.")
                    break

                # Решаем, нужно ли переводить (с учетом Smart Mode)
                need_update = self._should_translate(entry) if smart_mode else not entry.msgstr.strip()

                if need_update:
                    try:
                        # 1. Защищаем переменные
                        text_to_translate, placeholders = self.protect_placeholders(entry.msgid)
                        
                        # 2. Переводим
                        translated = translator.translate(text_to_translate)
                        
                        if translated:
                            # 3. Восстанавливаем переменные
                            entry.msgstr = self.restore_placeholders(translated, placeholders)
                            translated_count += 1
                            self.log(f"[{i+1}/{total}] ORIGINAL: {entry.msgid}")
                            self.log(f"[{i+1}/{total}] TRANSLATED: {entry.msgstr}")
                            self.log("-" * 30)
                        
                        time.sleep(1.1) 
                    except Exception as e:
                        self.log(f"⚠️ Error: {e}")
                        time.sleep(2)
                else:
                    self.log(f"⏭️ [{i+1}/{total}] Skipping...")

                self.update_progress((i + 1) / total)
                
                # Промежуточное сохранение
                if (i + 1) % 10 == 0:
                    po.save(self.file_path)

            po.save(self.file_path)
            self.log(f"✨ Done! Updated {translated_count} strings.")
            return True
        except Exception as e:
            self.log(f"🔥 Critical Error: {e}")
        finally:
            if po:
                po.save(self.file_path) # Сохранит ВСЕГДА при выходе из run
                self.log("💾 File state synchronized and saved.")
            return True