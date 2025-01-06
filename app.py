from flask import Flask, request, jsonify, render_template
import json
import re
import time
import random
from datetime import datetime

app = Flask(__name__)

# Load knowledge base from JSON file


def load_knowledge_base():
    with open('knowledge_base.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Enhanced response system


class MarketingChatbot:
    def __init__(self):
        self.knowledge_base = load_knowledge_base()
        self.conversation_history = {}

    def preprocess_text(self, text):
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def calculate_similarity(self, text1, text2):
        # Simple word overlap similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0

    def find_best_match(self, user_input):
        preprocessed_input = self.preprocess_text(user_input)
        best_match = None
        best_score = 0

        for category in self.knowledge_base:
            for qa_pair in self.knowledge_base[category]:
                similarity = self.calculate_similarity(preprocessed_input,
                                                       self.preprocess_text(qa_pair['question']))
                if similarity > best_score and similarity > 0.3:  # Threshold
                    best_score = similarity
                    best_match = qa_pair

        return best_match

    def get_response(self, user_input, session_id):
        # Initialize conversation history if needed
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        # Add user message to history
        self.conversation_history[session_id].append({
            'role': 'user',
            'message': user_input,
            'timestamp': datetime.now().isoformat()
        })

        # Find best matching response
        best_match = self.find_best_match(user_input)

        if best_match:
            response = best_match['answer']
            if isinstance(response, list):
                response = random.choice(response)
        else:
            # Handle unknown queries
            response = self.handle_unknown_query(user_input)

        # Add bot response to history
        self.conversation_history[session_id].append({
            'role': 'bot',
            'message': response,
            'timestamp': datetime.now().isoformat()
        })

        return response

    def handle_unknown_query(self, user_input):
        keywords = ['how', 'what', 'why', 'when', 'where', 'which']
        user_input_lower = user_input.lower()

        if any(keyword in user_input_lower for keyword in keywords):
            return ("I'm not sure about that specific question, but I'd be happy to help you "
                    "with digital marketing topics like SEO, content strategy, social media, "
                    "or marketing analytics. Could you rephrase your question?")

        return ("I'm here to help with digital marketing! You can ask me about topics like "
                "SEO, content marketing, social media strategy, email marketing, or analytics.")


# Initialize chatbot
chatbot = MarketingChatbot()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    user_input = data.get('user_input', '')
    session_id = data.get('session_id', 'default')

    # Simulate typing delay for more natural interaction
    time.sleep(0.5)

    response = chatbot.get_response(user_input, session_id)
    return jsonify({
        'response': response,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/get_history', methods=['POST'])
def get_history():
    session_id = request.json.get('session_id', 'default')
    return jsonify(chatbot.conversation_history.get(session_id, []))


@app.route('/clear_history', methods=['POST'])
def clear_history():
    session_id = request.json.get('session_id', 'default')
    if session_id in chatbot.conversation_history:
        chatbot.conversation_history[session_id] = []
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True, port=8080)
