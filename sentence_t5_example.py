from sentence_transformers import SentenceTransformer, util

# Load the model
model = SentenceTransformer("sentence-transformers/sentence-t5-base")

# Sample input sentence (symptoms or description)
input_sentence = "I have a fever, cough, and difficulty breathing."

# Encode the sentence
embedding = model.encode(input_sentence, convert_to_tensor=True)

print(embedding.shape)  # Check the output embedding size# Example disease descriptions
diseases = {
    "Flu": "Fever, cough, muscle pain, fatigue",
    "COVID-19": "Fever, cough, difficulty breathing, loss of taste",
    "Common Cold": "Sneezing, runny nose, sore throat, mild cough",
}

# Encode disease descriptions
disease_embeddings = {d: model.encode(desc, convert_to_tensor=True) for d, desc in diseases.items()}

# Find the most similar disease
similarities = {d: util.pytorch_cos_sim(embedding, emb)[0][0].item() for d, emb in disease_embeddings.items()}
predicted_disease = max(similarities, key=similarities.get)

print(f"Predicted Disease: {predicted_disease}")