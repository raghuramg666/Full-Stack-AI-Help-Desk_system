from sentence_transformers import SentenceTransformer, util
import json
from logs.logger_utils import get_logger

# Initialize logger and embedding model
logger = get_logger(__name__)
model = SentenceTransformer('models/all-MiniLM-L6-v2')


# Load knowledge base chunks
with open("embeddings/knowledge_chunks.json", "r", encoding="utf-8") as f:
    CHUNKS = json.load(f)

# Precompute embeddings for each chunk
EMBEDDINGS = [
    (chunk_text, chunk_cat, model.encode(chunk_text, convert_to_tensor=True))
    for chunk_text, chunk_cat in CHUNKS
]

# Mapping of category to its relevant data sources
CATEGORY_TO_SOURCES = {
    "password_reset": ["knowledge_base", "company_it_policies", "troubleshooting_database"],
    "software_installation": ["installation_guides", "knowledge_base", "troubleshooting_database"],
    "hardware_failure": ["knowledge_base", "company_it_policies", "troubleshooting_database"],
    "network_connectivity": ["knowledge_base", "company_it_policies", "troubleshooting_database"],
    "email_configuration": ["knowledge_base", "troubleshooting_database"],
    "security_incident": ["knowledge_base", "company_it_policies", "troubleshooting_database"],
    "policy_question": ["company_it_policies"],
    "general_inquiry": ["knowledge_base", "company_it_policies", "installation_guides", "troubleshooting_database"]
}

def retrieve_chunks(query: str, category: str = "general_inquiry"):
    """
    Retrieves top 3 semantically similar chunks based on the input query and category.
    """
    logger.info(f"Retrieving chunks for category: {category}")
    query_vec = model.encode(query, convert_to_tensor=True)
    sources = CATEGORY_TO_SOURCES.get(category, [])

    relevant = [
        (text, util.pytorch_cos_sim(query_vec, emb).item())
        for text, cat, emb in EMBEDDINGS if cat in sources
    ]
    top = sorted(relevant, key=lambda x: x[1], reverse=True)[:3]
    return [text for text, _ in top]
