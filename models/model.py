from sentence_transformers import SentenceTransformer
import os

# Load the model (this will download it if not already cached)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Target path inside your project
target_path = os.path.join("models", "all-MiniLM-L6-v2")

# Save the model
model.save(target_path)

print(f"✅ Model saved to: {target_path}")
