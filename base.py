from flask import Flask, render_template
import conceptnet_lite
from conceptnet_lite import Label, edges_for
from nrclex import NRCLex
from better_profanity import profanity 
from flask import request
import openai
import random
from flask import Flask, redirect, url_for, session, jsonify
import json
import os

conceptnet_lite.connect("/home/maneesh/Documents/adMaker/dataBase/conceptnet.db")

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load user data from JSON file
def load_users():
    try:
        with open('users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save user data to JSON file
def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file)

# Function to update user profile with the word in the users.json file
def add_word_update(email, word):
    with open('users.json', 'r') as file:
        users = json.load(file)

    if email in users:
        users[email].setdefault('word', []).append(word)

        with open('users.json', 'w') as file:
            json.dump(users, file, indent=4)

# Function to update user profile with an emotion in the users.json file
def add_emotion_update(email, word):
    with open('users.json', 'r') as file:
        users = json.load(file)

    if email in users:
        users[email].setdefault('emotion', []).append(word)

        with open('users.json', 'w') as file:
            json.dump(users, file, indent=4)

def add_stories_update(email, word):
    with open('users.json', 'r') as file:
        users = json.load(file)

    if email in users:
        users[email].setdefault('stories', []).append(word)

        with open('users.json', 'w') as file:
            json.dump(users, file, indent=4)

def get_emotion_words(word, emotion):
    # list of words to return
    emotion_words = []
    no_emotions = []

    # list of relations to search
    relations = ['related_to','form_of','is_a','part_of','used_for','capable_of','causes','has_subevent','has_first_subevent','has_prerequisite','has_property','synonym','antonym','distinct_from','derived_from','defined_as','has_context','similar_to','etymologically_related_to','receives_action']

    # check for profanity in word
    if profanity.contains_profanity(word) == True:
        print('Sorry, there is no information for this word')
        return []

    # get associated words
    usecases = []
    for i in relations:
        for e in edges_for(Label.get(text = word, language ='en').concepts, same_language = True):
            if(e.relation.name == i and e.start.text == word):
                if e.end.text not in usecases and profanity.contains_profanity(e.end.text) == False:
                    usecases.append(e.end.text.replace('_',' '))

        for e in edges_for(Label.get(text = word, language ='en').concepts, same_language = True):
            if(e.relation.name == i and e.end.text == word):
                if e.start.text not in usecases and profanity.contains_profanity(e.start.text) == False:
                    usecases.append(e.start.text.replace('_',' '))

    # check emotion of each word
    for word in usecases:
        emo_dict = NRCLex(word).affect_frequencies

        # add word to emotion_words list if it has the specified emotion
        if emotion in emo_dict.keys() and emo_dict[emotion] > 0:
            emotion_words.append(word)
        else:
            no_emotions.append(word) 

    return emotion_words, no_emotions

def generate_story(prompt, character, emotion):
    # set up API client
    openai.api_key = os.environ['API_KEY']

    # generate story
    response = openai.Completion.create(
        model="text-babbage-001",
        prompt=f"#prompt : pen #idea : A student is in an examination hall. He starts imagining his family members pressurising him to get good marks. Once he opens his pencil box and hold the pen, he feels confident and writes the exam really well. This depicts how a good pen that offers comfort while writing can ease the students pressures while writing an exam. #prompt : Air Conditioning #idea : A couple has a discussion on buying an Air conditioning. Wife buys the Air Conditioning without discussing with him. Husband advices her that she could have done some research before buying one. Then wife explains all the features the Air Conditioning provides which makes it best in the market. #prompt : Chocolate #idea : A small girl enters a grocery store with her mother. The mother looks tensed and worried while speaking to someone on the phone. The girl goes to the shop keeper and asks for a chocolate. She gives her toys one by one as money. The shop keeper gives her the chocolate and in return gives a small toy as change. The girl gives the chocolate to her mother and wishes Happy Birthday!. This makes the mother feel happy and hugs her daughter. #prompt : Bulb #idea : Husband and wife talk to each other in the video call. Husband is on an office trip. He gets a call from his boss and asks his wife to stay on line. While he is speaking to his boss he notices that his wife fell asleep. So he switches the lights off in his house with the help his mobile phone. This shows how smart bulbs are helpful. #prompt: Television #idea: A family of four is gathered around their television in the living room. They are watching a movie and eating popcorn. The youngest member of the family is so absorbed in the show that he hardly notices his siblings passing him popcorn and making funny comments about the actors. This shows how television brings an entire family together for some quality time. #prompt: Flower Vase #idea: A woman is having a tough day at work and is feeling low. She decides to take a break and goes to the nearby florist. She buys a beautiful flower vase and brings it home. She looks at the vase and smiles. She arranges the flowers in the vase to create a stunning bouquet. Looking at the vase and the flowers, she feels relaxed and happier. This illustrates how flowers in a vase can bring joy and peace to someone's day.#prompt: Photo frame #idea: A family is gathered together to celebrate the grandmother's 80th birthday. As a surprise, the family presents her with a photo frame. As grandmother looks at the frame, she starts reminiscing about the times spent with her family. This shows how a photo frame can evoke fond memories and bring joy to the elderly. #prompt: Suitcase as a bomb #idea: A young girl is travelling alone on a bus. She notices an unattended suitcase in the corner of the bus and gets suspicious. She immediately alerts the authorities who check the suitcase and find it to be a bomb. This illustrates how even the most innocuous objects can be used as a weapon of terror. #prompt: Travelling in a flight #idea: A family is travelling to another city in a flight. They are all excited to reach the destination and explore the new city. The family is looking out of the window and the little ones are asking questions about the birds and the clouds. This shows how travelling in a flight can be fun and exciting for the entire family.#prompt: Cool drink in Christmas celebration #idea: It is Christmas celebration and a family is gathered around the Christmas tree. They open their presents and enjoy the delicious Christmas feast. The little ones ask for a cool drink and the father brings out a can of soda from the refrigerator. The family cheers and enjoy the festive season with a cool drink in hand. This illustrates how a simple thing like a cool drink can add joy to a special occasion. #prompt: Generate a story advertising {prompt} with an emotion of {emotion} with charateristics of {character}",
        temperature=0.7,
        max_tokens=370,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # get generated text
    story = response["choices"][0]["text"]

    # return first 200 words of story
    return story


def get_story(word, emotion):
    stories = {}
    emotion_words, no_emotion_words = get_emotion_words(word, emotion)
    condition = 0

    if len(emotion_words) == 0:
        if len(no_emotion_words) > 3:
            # If there are no emotion words and no emotion words have a number greater than 3
            three_no_emotion_words = random.sample(no_emotion_words, 3)
            for i in three_no_emotion_words:
                stories[i] = generate_story(word, emotion, i)
            condition = 1
        else:
            # If there are no emotion words and no emotion words have a number less than or equal to 3
            for i in no_emotion_words:
                stories[i] = generate_story(word, emotion, i)
            condition = 2
    else:
        if len(emotion_words) > 3:
            # If there are emotion words and emotion words have a number greater than 3
            three_emotion_words = random.sample(emotion_words, 3)
            for i in three_emotion_words:
                stories[i] = generate_story(word, emotion, i)
            condition = 3
        else:
            # If there are emotion words and emotion words have a number less than or equal to 3
            for i in emotion_words:
                stories[i] = generate_story(word, emotion, i)
            condition = 4

    return stories

def emotion_words_list(word, emotion):
    emotion_words, no_emotion_words = get_emotion_words(word, emotion)
    if len(emotion_words) == 0:
        return no_emotion_words
    else:
        return emotion_words

#Home page
@app.route('/')
def index():
    word = request.args.get("word", "")
    emotion = request.args.get("emotion", "")
    status = ""
    if word and emotion:
        output_story = get_story(word, emotion)
        length = len(output_story)
    # if word:
    else:
        output_story = ""

        length = 0
    return render_template('index.html', output_story=output_story, length=length)

#signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = load_users()
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        
        if username in users:
            return render_template('signupfail.html')
        
        users[username] = {'password': password, 'name': name}
        save_users(users)
        return render_template('signupsuccessful.html')
    
    return render_template('signup.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Load the user data from JSON
        with open('users.json', 'r') as file:
            users = json.load(file)

        for user_email, user_data in users.items():
            if user_email == username and user_data['password'] == password:
                # If authentication succeeds, set session variables
                session['username'] = username
                session['name'] = user_data['name']
                session['word'] = user_data.get('word', [])
                session['emotion'] = user_data.get('emotion', [])
                session['stories'] = user_data.get('stories', {})
                # Redirect to the profile page
                return redirect(url_for('profile'))

        # If authentication fails, display error message on login page
        message = 'Invalid email or password'
        return render_template('login.html', message=message)

    return render_template('login.html', message=None)

#Profile page
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' in session and 'name' in session:
        username = session['username']
        name = session['name']
        word = session['word']
        emotion = session['emotion']
        # stories = session['stories']
        output_story = ""

        if request.method == 'POST':
            # Update the profile information
            word = request.form['word']
            emotion = request.form['emotion']
            print(word)
            print(emotion)
            status = ""
            if word and emotion:
                output_story = get_story(word, emotion)
            else:
                output_story = ""
            # session['word'] = word
            # session['emotion'] = emotion
            add_word_update(username, word)
            add_emotion_update(username, emotion)
            add_stories_update(username, output_story)

        return render_template('profile.html', name=name, output_story=output_story)

    # Redirect to the login page if not logged in
    return redirect(url_for('login'))


#History Page
@app.route('/history')
def history():
    if 'username' in session:
        username = session['username']

        # Load the user data from JSON
        with open('users.json', 'r') as file:
            users = json.load(file)

        if username in users:
            word = users[username].get('word', [])
            emotion = users[username].get('emotion', [])
            stories = users[username].get('stories', [])
            length = len(word)
            print(type(word))
            print(emotion)
            print(type(stories))
            return render_template('history.html', word=word, emotion=emotion, stories=stories, length=length)

    # Redirect to the login page if not logged in or user not found
    return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

#about page
@app.route('/aboutUs')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, port=5002)