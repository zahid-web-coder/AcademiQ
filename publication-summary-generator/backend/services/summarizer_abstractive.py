# services/summarizer_abstractive.py
import os
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

model = None
tokenizer = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
local_model_path = os.path.join("models", "t5-small")

def _local_model_is_complete(path: str) -> bool:
    needed = [
        "config.json",
        "generation_config.json",
        "pytorch_model.bin",
        "spiece.model",
        "tokenizer.json",
        "tokenizer_config.json"
    ]
    return all(os.path.exists(os.path.join(path, f)) for f in needed)

def load_model():
    global model, tokenizer
    if model is not None and tokenizer is not None:
        return

    # Try local first; if incomplete, pull from HF and save locally
    if _local_model_is_complete(local_model_path):
        print(f"📦 Loading T5 from local folder: {local_model_path}")
        tokenizer = T5Tokenizer.from_pretrained(local_model_path)
        model = T5ForConditionalGeneration.from_pretrained(local_model_path)
    else:
        print("⚠️ Local T5 incomplete/missing. Downloading t5-small…")
        tokenizer = T5Tokenizer.from_pretrained("t5-small")
        model = T5ForConditionalGeneration.from_pretrained("t5-small")
        os.makedirs(local_model_path, exist_ok=True)
        tokenizer.save_pretrained(local_model_path)
        model.save_pretrained(local_model_path)
        print("✅ T5 saved locally.")

    model.to(device)
    print(f"✅ T5 ready on {device}")

def abstractive_summary(text: str, max_length: int = 150) -> str:
    if not text or not text.strip():
        return "Error: Empty text input."
    load_model()

    prompt = "summarize: " + text.strip()
    inputs = tokenizer.encode(
        prompt,
        return_tensors="pt",
        max_length=512,
        truncation=True
    ).to(device)

    # keep outputs concise and non-repetitive
    adjusted_max = min(max_length, max(32, int(inputs.shape[1] * 0.75)))
    summary_ids = model.generate(
        inputs,
        max_length=adjusted_max,
        min_length=30,
        length_penalty=1.5,
        num_beams=4,
        no_repeat_ngram_size=3,
        early_stopping=True
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
