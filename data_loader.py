import os
import json
from pathlib import Path
from logs.logger_utils import get_logger

INPUT_FOLDER = "documents"
OUTPUT_FOLDER = "embeddings"
OUTPUT_FILE = "knowledge_chunks.json"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize logger
logger = get_logger("document_chunking")

# Files allowed for embedding
ALLOWED_FILES = {
    "company_it_policies.md",
    "installation_guides.json",
    "knowledge_base.md",
    "troubleshooting_database.json",
    "categories.json"
}

def chunk_markdown(file_path, category_name):
    """
    Splits a markdown file into chunks by top-level headers.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        raw_chunks = text.split("\n## ")
        chunks = [(chunk.strip(), category_name) for chunk in raw_chunks if len(chunk.strip()) > 20]
        logger.info(f"Processed markdown file: {file_path} with {len(chunks)} chunks.")
        return chunks
    except Exception as e:
        logger.error(f"Error processing markdown file {file_path}: {e}")
        return []

def chunk_json(file_path, category_name):
    """
    Flattens JSON objects and arrays into text chunks.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks = []
        if isinstance(data, dict):
            for key, val in data.items():
                if isinstance(val, list):
                    for item in val:
                        chunks.append((json.dumps(item, indent=2), category_name))
                else:
                    chunks.append((json.dumps(val, indent=2), category_name))
        elif isinstance(data, list):
            for item in data:
                chunks.append((json.dumps(item, indent=2), category_name))

        logger.info(f"Processed JSON file: {file_path} with {len(chunks)} chunks.")
        return chunks
    except Exception as e:
        logger.error(f"Error processing JSON file {file_path}: {e}")
        return []

def main():
    all_chunks = []
    logger.info("Starting document chunking process")

    for file in os.listdir(INPUT_FOLDER):
        try:
            if file not in ALLOWED_FILES:
                logger.warning(f"Skipping disallowed file: {file}")
                continue

            full_path = os.path.join(INPUT_FOLDER, file)
            ext = Path(file).suffix
            category_name = Path(file).stem

            if ext == ".md":
                chunks = chunk_markdown(full_path, category_name)
            elif ext == ".json":
                chunks = chunk_json(full_path, category_name)
            else:
                logger.warning(f"Unsupported file format skipped: {file}")
                continue

            all_chunks.extend(chunks)
        except Exception as e:
            logger.error(f"Error handling file {file}: {e}")

    try:
        output_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(all_chunks, out, indent=2)
        logger.info(f"Saved {len(all_chunks)} chunks to {output_path}")
        print(f"Done. Saved {len(all_chunks)} chunks to {output_path}")
    except Exception as e:
        logger.critical(f"Failed to write chunks to output: {e}")

if __name__ == "__main__":
    main()
