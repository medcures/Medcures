from flask import Flask, request, jsonify

app = Flask(__name__)

# Disease knowledge base
diseases = {
    "Flu": {
        "symptoms": ["headache", "fever", "cough", "tiredness"],
        "advice": "Drink fluids, rest, and take paracetamol if needed. Consult a doctor if fever persists."
    },
    "Food Poisoning": {
        "symptoms": ["stomach pain", "vomiting", "diarrhea", "fever"],
        "advice": "Stay hydrated, avoid solid food for some hours. Seek a doctor if severe vomiting or dehydration occurs."
    },
    "Migraine": {
        "symptoms": ["headache", "nausea", "sensitivity to light", "blurred vision"],
        "advice": "Rest in a dark, quiet room. Pain relievers may help. Consult a doctor if migraines are frequent."
    },
    "COVID-19": {
        "symptoms": ["fever", "cough", "tiredness", "loss of taste", "loss of smell"],
        "advice": "Isolate yourself, stay hydrated, and monitor oxygen levels. Contact healthcare if breathing difficulty occurs."
    }
}

# Store user symptoms in memory (⚠️ for demo — in production use session IDs)
user_symptoms = []

@app.route('/webhook', methods=['POST'])
def webhook():
    global user_symptoms
    req = request.get_json(silent=True, force=True)

    # Extract intent and query
    intent = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    query_text = req.get("queryResult", {}).get("queryText", "").lower()

    response_text = "Sorry, I didn’t understand. Can you repeat?"

    # ✅ Welcome Intent
    if intent == "Default Welcome Intent":
        user_symptoms = []  # reset session
        response_text = "Hello! I’m your health assistant 🤖. Please tell me your symptoms one by one."

    # ✅ Collect Symptoms
    elif intent == "GetSymptoms":
        if query_text not in ["that's it", "done", "no more", "finished"]:
            user_symptoms.append(query_text)
            response_text = f"Noted: {query_text}. Any other symptom? (say 'that's it' when finished)"
        else:
            # Analyze best matching disease
            best_match = None
            best_score = 0
            for disease, data in diseases.items():
                score = len(set(user_symptoms) & set(data["symptoms"]))
                if score > best_score:
                    best_score = score
                    best_match = disease

            if best_match:
                response_text = (
                    f"Based on your symptoms ({', '.join(user_symptoms)}), "
                    f"the most likely condition is **{best_match}**.\n\n"
                    f"👉 Advice: {diseases[best_match]['advice']}\n\n"
                    f"(⚠️ Note: This is only for awareness, not a medical diagnosis. Please consult a doctor.)"
                )
            else:
                response_text = "I couldn’t find a clear match. Please consult a healthcare professional."

            # Reset after conclusion
            user_symptoms = []

    return jsonify({"fulfillmentText": response_text})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
