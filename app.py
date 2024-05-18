from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Initialize the database
def init_db():
    with sqlite3.connect('chatbot.db') as conn:
        c = conn.cursor()
        conn.commit()

# Global state to keep track of the last action
user_state = {
    'expecting_email': False,
    'expecting_password': False,
    'email': None
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global user_state
    user_input = request.json.get('message').strip()
    response = ''

    if user_input.lower() == 'i want to login':
        response = 'Enter your email:'
        user_state['expecting_email'] = True
        user_state['expecting_password'] = False
        user_state['email'] = None
    elif user_state['expecting_email']:
        if '@' in user_input:
            user_state['email'] = user_input
            response = 'Enter your password:'
            user_state['expecting_email'] = False
            user_state['expecting_password'] = True
        else:
            response = 'Invalid email format. Please enter a valid email:'
    elif user_state['expecting_password']:
        save_user(user_state['email'], user_input)
        response = 'Login successful!'
        user_state['expecting_password'] = False
        user_state['email'] = None
    else:
        response = "I didn't understand that. Type 'I want to login' to start the login process."

    return jsonify({'response': response})

def save_user(email, password):
    with sqlite3.connect('chatbot.db') as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users( email TEXT, password TEXT)')
        c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
