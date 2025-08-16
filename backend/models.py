from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from huggingface_hub import login
import os
from dotenv import load_dotenv

def getBertSentiment(reviews: str, batch_size=64):
    load_dotenv()
    login(token=os.getenv("HUGGINGFACE_TOKEN"))
    checkpoint = "stat-learning/film-review_roberta" 
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device).eval()
    LABEL_MAP = {"0": "NEGATIVE", "1": "POSITIVE"}
    sentiments = []

    for i in range(0, len(reviews), batch_size):
        batch = reviews[i:i+batch_size]
        toks = tokenizer(batch,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(device)

        with torch.no_grad():
            logits = model(**toks).logits
        preds = logits.argmax(dim=-1).tolist()
        sentiments.extend([LABEL_MAP[str(p)] for p in preds])

    return sentiments