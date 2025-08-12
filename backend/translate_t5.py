import requests
import json
from transformers import MarianMTModel, MarianTokenizer, AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from huggingface_hub import login
import os
from dotenv import load_dotenv
from langdetect import detect
from langcodes import Language


# Hàm kiểm tra xem mô hình MarianMT có tồn tại cho ngôn ngữ không
def check_marian_model(lang_code):
    model_name = f"Helsinki-NLP/opus-mt-{lang_code}-en"
    try:
        response = requests.head(f"https://huggingface.co/{model_name}", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Hàm lấy danh sách ngôn ngữ từ Gist và lọc các ngôn ngữ được hỗ trợ bởi MarianMT
def fetch_supported_languages():
    gist_url = "https://api.github.com/gists/8eb57b065ea0b098d571"
    headers = {"Accept": "application/vnd.github+json"}
    
    try:
        response = requests.get(gist_url, headers=headers)
        response.raise_for_status()
        gist_data = response.json()
        
        file_content = gist_data['files']['ISO-639-1-language.json']['content']
        languages = json.loads(file_content)
        
        # Lọc các mã ngôn ngữ được hỗ trợ bởi MarianMT
        supported_codes = []
        for lang in languages:
            code = lang['code']
            if code != 'en' and check_marian_model(code):
                supported_codes.append(code)
        
        return supported_codes
    except requests.RequestException as e:
        print(f"Error fetching Gist: {e}")
        return ['vi', 'fr', 'es', 'zh', 'de', 'ja']  # Dự phòng nếu API thất bại

# Lấy danh sách ngôn ngữ được hỗ trợ
supported_languages = fetch_supported_languages()

def detect_and_translate(texts, lang_code=None):
    if isinstance(texts, str):
        texts = [texts]
    
    # Phát hiện ngôn ngữ
    if lang_code is None:
        try:
            lang_code = detect(texts[0])
        except:
            return [None] * len(texts)
    
    marian_lang_code = lang_code.split('-')[0]

    # Kiểm tra nếu ngôn ngữ là tiếng Anh
    if marian_lang_code == 'en':
        return texts

    # Kiểm tra xem mô hình MarianMT có hỗ trợ ngôn ngữ này không
    if marian_lang_code not in supported_languages:
        return [None] * len(texts)

    # Khởi tạo tokenizer và model cho ngôn ngữ cụ thể
    model_name = f"Helsinki-NLP/opus-mt-{marian_lang_code}-en"
    try:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
    except:
        return [None] * len(texts)

    # Tạo bản dịch cho toàn bộ batch
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=512,
            num_beams=4,
            early_stopping=True
        )

    translated_texts = [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
    return translated_texts

def translate_reviews(list_reviews):
    # Nhóm các review theo ngôn ngữ
    reviews_by_lang = {}
    for review in list_reviews:
        try:
            lang_code = detect(review)
            marian_lang_code = lang_code.split('-')[0]
            if marian_lang_code not in reviews_by_lang:
                reviews_by_lang[marian_lang_code] = []
            reviews_by_lang[marian_lang_code].append(review)
        except:
            # Nếu không phát hiện được ngôn ngữ, xử lý riêng
            reviews_by_lang.setdefault('unknown', []).append(review)

    translated_reviews = []
    for lang_code, reviews in reviews_by_lang.items():
        if lang_code == 'unknown':
            translated_reviews.extend([None] * len(reviews))
        else:
            translated_reviews.extend(detect_and_translate(reviews, lang_code))

    return translated_reviews