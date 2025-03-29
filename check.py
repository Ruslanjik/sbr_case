import cv2
import pytesseract
import numpy as np
import re

# Указываем путь к Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    
    if image is None:
        print("Ошибка: изображение не загружено.")
        return None

    # Перевод в серый
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Повышаем контрастность
    gray = cv2.convertScaleAbs(gray, alpha=2, beta=20)

    # Убираем шум
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Применяем адаптивную бинаризацию
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Сохраняем обработанное изображение для проверки
    cv2.imwrite("processed_receipt.jpg", gray)
    
    return gray

def extract_text_from_receipt(image_path):
    processed_image = preprocess_image(image_path)
    if processed_image is None:
        return ""

    # Пробуем распознать текст
    text = pytesseract.image_to_string(processed_image, lang='eng')
    print("\n=== Распознанный текст ===\n", text)
    
    return text

def parse_receipt_text(text):
    items = []
    total = 0.0

    # Поиск цен в формате 18K 92.21 или 18.99
    price_pattern = re.compile(r'(\d{1,3}[.,]\d{2})')

    matches = price_pattern.findall(text)
    if matches:
        items = [float(price.replace(',', '.')) for price in matches]

    # Определяем общую сумму (берем максимальную цену)
    total = max(items) if items else 0.0

    return items, total

def split_total_among_people(total):
    try:
        # Запрос количества людей
        num_people = int(input("Введите количество людей для разделения суммы: "))
        if num_people <= 0:
            print("Ошибка: количество людей должно быть больше 0.")
            return total

        # Разделяем сумму
        amount_per_person = total / num_people
        print(f"Каждый человек должен заплатить: {amount_per_person:.2f} доллара/евро.")
        return amount_per_person
    except ValueError:
        print("Ошибка: введено некорректное число.")
        return total

# Запуск
image_path = "check.webp"
text = extract_text_from_receipt(image_path)
items, total = parse_receipt_text(text)

print("\n=== Итог ===")
print("Распознанные цены:", items)
print("Общая сумма:", total)

# Разделяем общую сумму на количество людей
split_total_among_people(total)
