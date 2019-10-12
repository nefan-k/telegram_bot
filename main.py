import telebot
import requests
import random
import html
#import re
#from telebot import types # проверить нужность

api_url = 'https://opentdb.com/api.php'
req = requests.get(api_url, params={'amount': 1, 'difficulty': 'easy', 'type': 'multiple'}).json()
token = ''
bot = telebot.TeleBot(token)
states = {}
level = {}
score = {}
correct_answers = {} 
answers = {}
MAIN_STATE = 'main'
QUESTION_STATE = 'question_handler'
COMPLEXITY_STATE = 'complexity_handler'
AMOUNT = 1
TYPE = 'multiple'
DEFEAT_POINTS = 1
level_points = {'easy': 1, 'medium': 2, 'hard': 3}
#users_id, current_id = [], ""

def victories (user, scores):
    if user in score:
        score[user]['victories'] += level_points[scores]
    else: 
        score[user] = {'victories': 0, 'defeats': 0}
        score[user]['victories'] += level_points[scores]
    print(score) # убрать

def defeats (user):
    if user in score:
        score[user]['defeats'] += DEFEAT_POINTS
    else: 
        score[user] = {'victories': 0, 'defeats': 0}
        score[user]['defeats'] += DEFEAT_POINTS
    print(score) # убрать

@bot.message_handler(func=lambda message:states.get(message.from_user.id, MAIN_STATE) == MAIN_STATE)
def main_handler(message):
    if message.from_user.id not in level:
        level[message.from_user.id] = 'easy'
    if message.from_user.id not in score:
        score[message.from_user.id] = {'victories': 0, 'defeats': 0}  
    if 'quest' in message.text.lower():
        response = requests.get(api_url, params={'amount': AMOUNT, 'category': None, 'difficulty': level[message.from_user.id], 'type': TYPE}).json()
        correct_answers[message.from_user.id] = html.unescape(response['results'][0]['correct_answer'])
        answers[message.from_user.id] = [html.unescape(response['results'][0]['correct_answer'])] + [html.unescape(i) for i in response['results'][0]['incorrect_answers']]
        print(correct_answers)
        print(answers)
        random.shuffle(answers[message.from_user.id])
        random.shuffle(answers[message.from_user.id])
        question = str(html.unescape(response['results'][0]['question'])) + ': '
        for i in answers[message.from_user.id]: # join
            question += str(i)+'; '
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True, selective=True)
        buttons = []
        for answer in answers[message.from_user.id]:
            buttons.append(telebot.types.KeyboardButton(answer))
        markup.add(*buttons)
        bot.send_message(message.from_user.id, question[:-2], reply_markup=markup)
        states[message.from_user.id] = QUESTION_STATE
    elif message.text == '/start':
        bot.send_message(message.from_user.id, 'It\'s a bot-game "Who Wants to Be a Millionaire?"')
        bot.send_message(message.from_user.id, 'I can ask interesting questions, change the level of difficulty and show the score')
        score[message.from_user.id] = {'victories': 0, 'defeats': 0}
    elif ('hi' in message.text.lower()) or ('hello' in message.text.lower()):
        bot.send_message(message.from_user.id, 'Hello, ' + message.from_user.first_name + '!')
    elif ('level' in message.text.lower()) or ('difficult' in message.text.lower()) or ('complex' in message.text.lower()):
        markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True, selective=True)
        kb1 = telebot.types.KeyboardButton('easy')
        kb2 = telebot.types.KeyboardButton('medium')
        kb3 = telebot.types.KeyboardButton('hard')
        markup.add(kb1, kb2, kb3)
        bot.send_message(message.from_user.id, 'The current level of difficulty is ' + level[message.from_user.id] + '. Select a new level of difficulty: easy, medium or hard', reply_markup=markup)
        states[message.from_user.id] = COMPLEXITY_STATE
    elif 'score' in message.text.lower():
        bot.send_message(message.from_user.id, 'victories: ' + str(score[message.from_user.id]['victories']) + ' / ' + 'defeats: '  + str(score[message.from_user.id]['defeats']))
    else:
        bot.reply_to(message, "I don't understand you")

@bot.message_handler(func=lambda message:states.get(message.from_user.id, MAIN_STATE) == QUESTION_STATE)
def question(message):
    if message.text == correct_answers[message.from_user.id]:
        bot.send_message(message.from_user.id, "That's right!")
        victories(message.from_user.id, level[message.from_user.id])
        states[message.from_user.id] = MAIN_STATE
    elif message.text in answers[message.from_user.id] and message.text != correct_answers[message.from_user.id]:
        bot.send_message(message.from_user.id, 'Wrong!:( Correct answer is ' + correct_answers[message.from_user.id])
        defeats(message.from_user.id)
        states[message.from_user.id] = MAIN_STATE
    else:
        bot.reply_to(message, "I don't understand you")

@bot.message_handler(func=lambda message:states.get(message.from_user.id, MAIN_STATE) == COMPLEXITY_STATE)
def complexity(message):
    if message.text == 'easy':
        bot.send_message(message.from_user.id, 'OK! There will be easy questions:)')
        level[message.from_user.id] = 'easy'
        states[message.from_user.id] = MAIN_STATE
    elif message.text == 'medium':
        bot.send_message(message.from_user.id, 'There will be questions of average complexity and double points for the victory!')
        level[message.from_user.id] = 'medium'
        states[message.from_user.id] = MAIN_STATE
    elif message.text == 'hard':
        bot.send_message(message.from_user.id, 'There will be difficult questions and triple points for the victory!')
        level[message.from_user.id] = 'hard'
        states[message.from_user.id] = MAIN_STATE
    else:
        bot.reply_to(message, "I don't understand you")
   
bot.polling()
