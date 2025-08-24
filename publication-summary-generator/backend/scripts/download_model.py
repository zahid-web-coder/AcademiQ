import os
from transformers import T5Tokenizer, T5ForConditionalGeneration

model_name = "t5-small"
save_path = os.path.join("models", model_name)

print(f"📦 Downloading {model_name} model and tokenizer...")

try:
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    print("✅ Tokenizer downloaded")

    model = T5ForConditionalGeneration.from_pretrained(model_name)
    print("✅ Model downloaded")

    os.makedirs(save_path, exist_ok=True)
    tokenizer.save_pretrained(save_path)
    model.save_pretrained(save_path)

    print(f"💾 Saved to {save_path}")
except Exception as e:
    print(f"❌ Download failed: {e}")
