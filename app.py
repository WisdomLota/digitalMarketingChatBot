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
        self.threshold = 0.5  # Increased threshold for better matching

    def preprocess_text(self, text):
        """Enhanced text preprocessing"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove common stop words that don't affect meaning
        stop_words = {'the', 'a', 'an', 'and', 'or',
                      'but', 'in', 'on', 'at', 'to', 'for', 'of'}
        return ' '.join(word for word in text.split() if word not in stop_words)

    def calculate_similarity(self, text1, text2):
        """Improved similarity calculation"""
        # Convert texts to sets of words
        words1 = set(text1.split())
        words2 = set(text2.split())

        # Calculate Jaccard similarity for words
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        word_similarity = len(intersection) / len(union) if union else 0

        # Calculate sequence matching
        def get_ngrams(text, n):
            words = text.split()
            return set(' '.join(words[i:i+n]) for i in range(len(words)-n+1))

        # Get bigrams and trigrams
        bigrams1 = get_ngrams(text1, 2)
        bigrams2 = get_ngrams(text2, 2)
        trigrams1 = get_ngrams(text1, 3)
        trigrams2 = get_ngrams(text2, 3)

        # Calculate n-gram similarities
        bigram_similarity = len(bigrams1.intersection(
            bigrams2)) / len(bigrams1.union(bigrams2)) if bigrams1 and bigrams2 else 0
        trigram_similarity = len(trigrams1.intersection(
            trigrams2)) / len(trigrams1.union(trigrams2)) if trigrams1 and trigrams2 else 0

        # Weight the similarities
        final_similarity = (
            0.4 * word_similarity +
            0.4 * bigram_similarity +
            0.2 * trigram_similarity
        )

        return final_similarity

    def find_best_match(self, user_input):
        """Enhanced matching logic"""
        preprocessed_input = self.preprocess_text(user_input)
        best_matches = []

        # First, try exact matches
        for category in self.knowledge_base:
            for qa_pair in self.knowledge_base[category]:
                if self.preprocess_text(qa_pair['question']) == preprocessed_input:
                    return qa_pair

                similarity = self.calculate_similarity(
                    preprocessed_input,
                    self.preprocess_text(qa_pair['question'])
                )
                if similarity > self.threshold:
                    best_matches.append((similarity, qa_pair))

        # Sort by similarity and get top match
        best_matches.sort(reverse=True, key=lambda x: x[0])
        return best_matches[0][1] if best_matches else None

    def get_response(self, user_input, session_id):
        """Enhanced response generation"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        # Log user input
        self.conversation_history[session_id].append({
            'role': 'user',
            'message': user_input,
            'timestamp': datetime.now().isoformat()
        })

        # Special handling for button questions
        button_questions = {
            "what are the most important seo ranking factors",
            "what types of content should i create",
            "what is the best time to post on social media",
            "what are email marketing best practices",
            "what marketing metrics should i track"
        }

        preprocessed_input = self.preprocess_text(user_input)
        if preprocessed_input in {self.preprocess_text(q) for q in button_questions}:
            # Direct lookup for button questions
            for category in self.knowledge_base:
                for qa_pair in self.knowledge_base[category]:
                    if self.preprocess_text(qa_pair['question']) == preprocessed_input:
                        response = qa_pair['answer']
                        break
        else:
            # Regular matching for other questions
            best_match = self.find_best_match(user_input)
            response = best_match['answer'] if best_match else self.handle_unknown_query(
                user_input)

        # Handle list responses
        if isinstance(response, list):
            response = random.choice(response)

        # Log bot response
        self.conversation_history[session_id].append({
            'role': 'bot',
            'message': response,
            'timestamp': datetime.now().isoformat()
        })

        return response

    def handle_unknown_query(self, user_input):
        """Improved unknown query handling"""
        user_input_lower = self.preprocess_text(user_input)

        # Define topic keywords
        topics = {
            'seo': ['seo', 'search engine', 'ranking', 'backlink', 'keyword'],
            'content': ['content', 'blog', 'article', 'video', 'post'],
            'social': ['social', 'facebook', 'instagram', 'twitter', 'linkedin'],
            'email': ['email', 'newsletter', 'campaign', 'subscriber'],
            'analytics': ['analytics', 'metric', 'measure', 'track', 'report']
        }

        # Try to identify the topic
        for topic, keywords in topics.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return (f"I understand you're asking about {topic.upper()}. Could you please "
                        f"rephrase your question more specifically? For example, try asking "
                        f"about best practices, strategies, or specific techniques in {topic}.")

        return ("I'm here to help with digital marketing! Try asking specific questions about:\n"
                "- SEO strategies and optimization\n"
                "- Content marketing and planning\n"
                "- Social media marketing\n"
                "- Email marketing campaigns\n"
                "- Analytics and performance tracking")


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
