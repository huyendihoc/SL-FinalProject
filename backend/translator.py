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


# Get supported languages list
with open("../data/supported_lang.json", 'r') as f:
    supported_languages = json.load(f)['lang']

def detect_and_translate(texts, lang_code=None):
    if isinstance(texts, str):
        texts = [texts]
    
    # Detect language
    if lang_code is None:
        try:
            lang_code = detect(texts[0])
        except:
            return [None] * len(texts)
    
    marian_lang_code = lang_code.split('-')[0]

    # Check if the language is English
    if marian_lang_code == 'en':
        return texts

    # Check if the language is supported
    if marian_lang_code not in supported_languages:
        return texts

    # Initialize the model and tokenizer
    model_name = f"Helsinki-NLP/opus-mt-{marian_lang_code}-en"
    try:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
    except:
        return [None] * len(texts)

    # Create translations for the batch of texts
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
    # Group reviews by detected language
    reviews_by_lang = {}
    for review in list_reviews:
        try:
            lang_code = detect(review)
            marian_lang_code = lang_code.split('-')[0]
            if marian_lang_code not in reviews_by_lang:
                reviews_by_lang[marian_lang_code] = []
            reviews_by_lang[marian_lang_code].append(review)
        except:
            reviews_by_lang.setdefault('unknown', []).append(review)

    translated_reviews = []
    for lang_code, reviews in reviews_by_lang.items():
        if lang_code == 'unknown':
            translated_reviews.extend([None] * len(reviews))
        else:
            translated_reviews.extend(detect_and_translate(reviews, lang_code))

    return translated_reviews