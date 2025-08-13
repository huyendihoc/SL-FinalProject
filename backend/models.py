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

def getBertSentiment(reviews: str):
    load_dotenv()
    login(token=os.getenv("HUGGINGFACE_TOKEN"))
    checkpoint = "stat-learning/film-review_roberta" 
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint)

    inputs = tokenizer(reviews, padding=True, truncation=True, max_length=512, return_tensors="pt")

    # Run inference
    with torch.no_grad():
        logits = model(**inputs).logits

    label_map = {
        "0": "NEGATIVE",
        "1": "POSITIVE"
    }

    # Get predicted classes
    predicted_class_ids = logits.argmax(dim=-1).tolist()
    predicted_classes = [label_map[str(id)] for id in predicted_class_ids]
    return predicted_classes