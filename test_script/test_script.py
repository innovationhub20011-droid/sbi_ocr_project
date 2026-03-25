import os
import re
import pandas as pd
import requests
from jiwer import cer, wer
from tqdm import tqdm

# CONFIG
API_URL = "http://127.0.0.1:8000/extract/text/handwritten_text"
IMAGE_FOLDER = "./images"
CSV_FILE = "labels.csv"

# Load CSV
df = pd.read_csv(CSV_FILE)
df.columns = [col.strip().lower() for col in df.columns]

IMAGE_COL = "filename"
TEXT_COL = "text"

total_cer = 0
total_wer = 0
count = 0
exact_match = 0

results = []

# -------------------------------
# CLEANING FUNCTIONS
# -------------------------------

def clean_text(text):
    if not isinstance(text, str):
        return ""

    text = text.lower()

    # remove xml tags like <text>
    text = re.sub(r'</?text>', '', text)

    # remove endpoint/debug junk
    text = re.sub(r'\[.*?\]', '', text)

    # remove markdown (**text**)
    text = re.sub(r'\*\*.*?\*\*', '', text)

    # remove punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def is_garbage(pred, gt):
    if pred == "":
        return True

    # very long vs GT → likely hallucination
    if len(pred) > 4 * len(gt):
        return True

    # common LLM junk
    bad_phrases = ["you are", "i am", "step", "extract"]
    if any(p in pred for p in bad_phrases):
        return True

    return False


# -------------------------------
# MAIN LOOP
# -------------------------------

for _, row in tqdm(df.iterrows(), total=len(df)):
    image_name = row[IMAGE_COL]
    true_text = clean_text(str(row[TEXT_COL]))

    image_path = os.path.join(IMAGE_FOLDER, image_name)

    if not os.path.exists(image_path):
        print(f"Missing: {image_path}")
        continue

    try:
        with open(image_path, "rb") as f:
            files = {
                "file": (image_name, f, "image/jpeg")
            }

            response = requests.post(API_URL, files=files)

        if response.status_code != 200:
            print(f"API failed: {image_name}")
            continue

        data = response.json()

        # Extract prediction
        pages = data.get("pages", [])
        pred_text = " ".join(
            page.get("extracted_text", "").strip()
            for page in pages
        )

        pred_text = clean_text(pred_text)

        # -----------------------
        # METRICS
        # -----------------------

        if is_garbage(pred_text, true_text):
            sample_cer = 1.0
            sample_wer = 1.0
        else:
            sample_cer = cer(true_text, pred_text)
            sample_wer = wer(true_text, pred_text)

            # HARD CAP (important)
            sample_cer = min(sample_cer, 1.0)
            sample_wer = min(sample_wer, 1.0)

        if true_text == pred_text:
            exact_match += 1

        total_cer += sample_cer
        total_wer += sample_wer
        count += 1

        results.append({
            "image": image_name,
            "ground_truth": true_text,
            "prediction": pred_text,
            "cer": sample_cer,
            "wer": sample_wer
        })

    except Exception as e:
        print(f"Error: {image_name} -> {e}")

# -------------------------------
# FINAL RESULTS
# -------------------------------

if count == 0:
    print("No images processed!")
else:
    avg_cer = total_cer / count
    avg_wer = total_wer / count
    accuracy = (1 - avg_cer) * 100
    exact_acc = (exact_match / count) * 100

    print("\n===== FINAL RESULTS =====")
    print(f"Images processed: {count}")
    print(f"Average CER: {avg_cer:.4f}")
    print(f"Average WER: {avg_wer:.4f}")
    print(f"Accuracy (%): {accuracy:.2f}")

# Save results
pd.DataFrame(results).to_csv("ocr_results.csv", index=False)
print("Saved: ocr_results.csv")