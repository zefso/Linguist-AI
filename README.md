# Linguist AI v1.2.0

Professional AI-powered tool for `.po` file translation.

## 📖 User Guide (How to use)

### 1. File Selection
- Launch the application.
- Click the **Browse** button and select your `.po` file (e.g., `django.po`).
- The application will automatically create a backup (`.bak`) of your file.

### 2. Configure Settings
- **Target Language:** Choose the language you want to translate your project into from the dropdown menu.
- **Smart Update (Toggle):** - **ON (Recommended):** The app will skip strings already translated in the correct language. If it detects a different language, it will overwrite it.
  - **OFF:** The app will only translate completely empty strings.

### 3. Translation Process
- Click the **START** button to begin.
- You will see the **Original Text** and **Translated Text** appearing in the activity log.
- Use the **STOP** button if you need to pause. The app will finish the current string and save all progress before stopping.

### 4. Results
- Once finished, a success message will appear.
- Your `.po` file is now updated and ready for compilation (`msgfmt` or `compilemessages`).

## ⚙️ Requirements
If you are running from source:
- Python 3.10+
- Libraries: `customtkinter`, `polib`, `deep-translator`, `langdetect`

## 🛠 Developer Notes
- **Placeholder Safety:** The app automatically protects Django/Python variables like `{count}` or `%s` so the AI won't break your code logic.
- **Safe Saving:** Every 5 translations are auto-saved to prevent data loss.