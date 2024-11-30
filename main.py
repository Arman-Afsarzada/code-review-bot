import io
from zipfile import ZipFile
from decouple import config
from telebot import TeleBot
import pycodestyle
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load the tokenizer and model (Salesforce CodeT5)
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5-base")

# Load Telegram Token from .env
TOKEN = config('TELEGRAM_TOKEN')

def create_report(report_path, contents):
    with open(report_path, "w") as file:
        file.write(contents)
    return report_path

def check_pep8_compliance(file_path):
    style = pycodestyle.StyleGuide()
    report = style.check_files([file_path])

    if report.total_errors == 0:
        return "Code is PEP8 compliant!"

    issues = []
    for line in report.get_statistics():
        issues.append(line)

    return f"Found {report.total_errors} PEP8 issues:\n" + "\n".join(issues)

def get_code_review_suggestions(code: str) -> str:
    # Tokenize and encode the code input
    inputs = tokenizer(code, return_tensors="pt", truncation=True, padding=True, max_length=512)
    # Generate analysis using CodeT5 model
    output = model.generate(inputs["input_ids"], max_length=512)

    # Decode the model's output into human-readable text
    decoded_output = tokenizer.decode(output[0], skip_special_tokens=True)
    return decoded_output

def process_file(file) -> str:
    temp_file_path = 'temp_file.py'

    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file)

    # Check for PEP8 compliance
    pep8_report = check_pep8_compliance(temp_file_path)

    # Read the code from the file for model analysis
    with open(temp_file_path, 'r') as temp_file:
        code = temp_file.read()

    # Get suggestions from the model
    model_suggestions = get_code_review_suggestions(code)

    # Create the report by combining PEP8 issues and model suggestions
    report = create_report("report.txt", f"{pep8_report}\n\nModel Suggestions:\n{model_suggestions}")
    return report

def is_python_code(file_content):
    """
    Check if the file content resembles Python code.
    """
    try:
        compile(file_content, "<string>", "exec")
        return True
    except SyntaxError:
        return False

def process_archive(zip_file):
    with ZipFile(io.BytesIO(zip_file), 'r') as archive:
        all_reports = []

        for file in archive.namelist():
            if file.endswith('.py') or file.endswith('.txt'):  # Process both .py and .txt files
                with archive.open(file) as nested_file:
                    file_contents = nested_file.read()

                    # Check if the .txt file contains Python code
                    if not file.endswith('.py') and is_python_code(file_contents.decode()):
                        file = file.replace('.txt', '.py')  # Treat the .txt file as .py for processing

                    # Write the file temporarily to check it
                    temp_file_path = 'temp_file.py'
                    with open(temp_file_path, 'wb') as temp_file:
                        temp_file.write(file_contents)

                    # Check the file for PEP8 compliance
                    result_report = check_pep8_compliance(temp_file_path)
                    all_reports.append(f"File: {file}\n{result_report}\n\n")

            else:
                all_reports.append(f"File: {file} is not a Python file and was skipped.\n")

        # Combine the reports from all files
        report = create_report("report.txt", "\n".join(all_reports))
        return report


bot = TeleBot(TOKEN)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    if message.document.file_name.endswith('.zip'):
        result_report = process_archive(downloaded_file)
        r_type = "архив"
    else:
        result_report = process_file(downloaded_file)
        r_type = "файл"

    bot.reply_to(message, f"Ваш {r_type} был обработан, результаты прикреплены к сообщению.")
    with open(result_report, "rb") as report_file:
        bot.send_document(chat_id=message.chat.id, document=report_file)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Привет! Я бот для проверки проектов. Отправьте мне файл или архив для обработки.")


@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    bot.reply_to(message, "Я не знаю, что делать с этим. Пожалуйста, отправьте мне файл или архив для обработки.")


if __name__ == '__main__':
    print("Bot started")
    bot.infinity_polling()
