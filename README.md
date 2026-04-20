# SBI OCR Vision API

FastAPI service for OCR and structured data extraction from banking and identity documents using an Ollama-hosted vision model. The project accepts uploaded images and some PDFs, sends them to a vision LLM with document-specific prompts, stores extracted results in SQLite by default, and exposes retrieval APIs for selected document categories.

## What this project does

This API supports:

- Structured extraction for:
  - PAN card
  - Aadhaar card
  - Passport
  - Driving license
  - Voter ID
  - SBI account opening form page 1
  - SBI account opening form page 2
- OCR extraction for text-heavy documents:
  - Handwritten text
  - Digital text
  - Miscellaneous text
- Persistence of extracted results into a database
- Raw model output logging to `data/raw_model_output.txt`
- Basic evaluation script for handwritten OCR samples in `test_script/`

## High-level flow

1. A client uploads an image or PDF to a FastAPI endpoint.
2. The file is converted to base64 image content.
3. PAN and Aadhaar uploads are first validated with the local document-classification model.
4. A prompt specific to the document type is sent to an Ollama vision model through LangChain.
5. The response is parsed into JSON or plain OCR text.
6. Supported results are saved through SQLAlchemy repositories.
7. Raw model output is appended to `data/raw_model_output.txt` for inspection/debugging.

## Tech stack

- Python
- FastAPI
- SQLAlchemy
- LangChain
- Ollama
- Pillow
- OpenCV
- pypdfium2
- SQLite by default

## Project structure

```text
sbi_ocr_project/
├── main.py                          # FastAPI app and route registration
├── controllers/                     # Route-level handlers
├── extractors/                      # Extraction logic per document type
├── prompts/                         # Prompt templates and target schemas
├── services/                        # File conversion and persistence orchestration
├── llm/                             # Ollama client, inference, parsing, logging
├── db/                              # Database session and repositories
├── models/                          # SQLAlchemy models
├── schemas/                         # Pydantic request/data validation models
├── utils/                           # Endpoint-to-model routing helpers
├── data/                            # SQLite DB and raw model output log
├── test_script/                     # OCR evaluation script and sample images
├── requirements.txt
└── .env
```

## Requirements

- Python 3.10+
- An Ollama server reachable from this app
- A vision-capable model pulled in Ollama, for example `llama3.2-vision:11b`

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Optional dependencies for the evaluation script in `test_script/test_script.py` are not listed in `requirements.txt`. Install them separately if you want to run that script:

```bash
pip install pandas requests jiwer tqdm
```

### 3. Configure environment variables

Example `.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision:11b
OLLAMA_STREAM=false
```

Supported environment variables:

- `OLLAMA_BASE_URL`: required unless `OLLAMA_HOST` is set
- `OLLAMA_HOST`: fallback to Ollama base URL
- `OLLAMA_MODEL`: default model used for all extraction routes
- `OLLAMA_TEMPERATURE`: optional, defaults to `0`
- `OLLAMA_NUM_PREDICT`: optional, defaults to `2048`
- `OCR_DB_PATH`: optional SQLAlchemy database URL; defaults to `sqlite:///data/ocr_records.db`

### 4. Start Ollama

Make sure Ollama is running and the configured model is available:

```bash
ollama serve
ollama pull llama3.2-vision:11b
```

### 5. Start the API

```bash
uvicorn main:app --reload
```

The API will be available at:

- `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

## API endpoints

### Extraction endpoints

| Endpoint | Purpose | Accepted files | Stored in DB |
|---|---|---|---|
| `POST /extract/pan` | Extract PAN details | PNG, JPG, JPEG | Yes |
| `POST /extract/aadhaar` | Extract Aadhaar details | PNG, JPG, JPEG | Yes |
| `POST /extract/passport` | Extract passport details | PNG, JPG, JPEG | Yes |
| `POST /extract/driving-license` | Extract driving license details | PNG, JPG, JPEG | Yes |
| `POST /extract/voter-id` | Extract voter ID details | PNG, JPG, JPEG | Yes |
| `POST /extract/text/handwritten_text` | OCR handwritten pages | PDF, PNG, JPG, JPEG | Yes |
| `POST /extract/text/digital_text` | OCR digital text pages | PDF, PNG, JPG, JPEG | Yes |
| `POST /extract/text/miscellaneous_text` | OCR miscellaneous text pages | PDF, PNG, JPG, JPEG | Yes |
| `POST /extract/account-opening/page1` | Extract SBI account opening form page 1 | PNG, JPG, JPEG | Yes |
| `POST /extract/account-opening/page2` | Extract SBI account opening form page 2 | PNG, JPG, JPEG | No |

### Retrieval endpoints

| Endpoint | Purpose |
|---|---|
| `GET /retrieve/pan/all` | Return saved PAN records |
| `GET /retrieve/aadhaar/all` | Return saved Aadhaar records |
| `GET /retrieve/text/handwritten_text/all` | Return saved handwritten OCR records |
| `GET /retrieve/text/digital_text/all` | Return saved digital OCR records |
| `GET /retrieve/text/miscellaneous_text/all` | Return saved miscellaneous OCR records |

Note:

- Retrieval routes are currently exposed only for PAN, Aadhaar, and text-document OCR tables.
- Passport, driving license, voter ID, and account-opening retrieval routes are not currently implemented in `main.py`.

## Example requests

### PAN extraction

```bash
curl -X POST "http://127.0.0.1:8000/extract/pan" \
  -F "file=@/absolute/path/to/pan_card.jpg"
```

### Handwritten OCR extraction

```bash
curl -X POST "http://127.0.0.1:8000/extract/text/handwritten_text" \
  -F "file=@/absolute/path/to/document.pdf"
```

### Retrieve all PAN records

```bash
curl "http://127.0.0.1:8000/retrieve/pan/all"
```

## Database behavior

On startup, the app runs `Base.metadata.create_all(bind=engine)`, so tables are created automatically if they do not already exist.

By default, the project writes to:

```text
data/ocr_records.db
```

Current model coverage includes:

- `pan_card_details`
- `aadhaar_card_details`
- `passport_details`
- `driving_license_details`
- `voter_id_details`
- `handwritten_text_ocr_details`
- `digital_text_ocr_details`
- `miscellaneous_text_ocr_details`
- `account_forms`
- `account_form_pages`

## Special handling in this codebase

### Model selection

All OCR endpoints use the default model configured in `OLLAMA_MODEL`.

### PDF support

Text-document OCR endpoints accept PDFs. Pages are rendered to images with `pypdfium2` before being sent to the vision model.

### OCR cleanup

The text-document OCR path includes cleanup logic to reduce repetition loops and broken output before persistence.

### Raw output logging

Every model response is appended to:

```text
data/raw_model_output.txt
```

This is useful for prompt debugging and parser troubleshooting.

## Account opening forms

### Page 1

`POST /extract/account-opening/page1`:

- extracts structured fields from the uploaded image
- creates a row in `account_forms`
- creates a related row in `account_form_pages`
- returns the generated `form_id`

### Page 2

`POST /extract/account-opening/page2`:

- extracts structured fields from the uploaded image
- returns JSON data only
- does not currently persist results to the database

## Evaluation script

The repository includes `test_script/test_script.py` for evaluating handwritten OCR output against labeled samples.

It:

- posts images to `http://127.0.0.1:8000/extract/text/handwritten_text`
- compares predictions with `labels.csv`
- computes CER and WER
- writes results to `test_script/ocr_results.csv`

Run it from inside `test_script/`:

```bash
cd test_script
python test_script.py
```

## Current limitations

- The project depends on an external Ollama server and available model weights.
- `OLLAMA_STREAM` exists in `.env`, but the current code path does not use it directly.
- `OLLAMA_MODEL_TEXT_EXTRACTION` is no longer used by the app.
- Retrieval endpoints are incomplete for several stored document types.
- The evaluation script depends on packages that are not included in `requirements.txt`.
- Error handling for malformed model responses is basic and often falls back to empty output.

## Development notes

- Main application entry: `main.py`
- Default DB path: `data/ocr_records.db`
- Raw model log: `data/raw_model_output.txt`
- Prompts live under `prompts/`
- Database repositories live under `db/repositories/`
