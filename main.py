import telebot
import requests
import random
import html
import os

api_url = 'https://opentdb.com/api.php'
req = {}
req_category = requests.get('https://opentdb.com/api_category.php').json()
token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)
states = {}
level = {}
score = {}
categories_dict= {'Random Category': None}
category_id = {}
correct_answers = {} 
answers = {}
MAIN_STATE = 'main'
QUESTION_STATE = 'question_handler'
COMPLEXITY_STATE = 'complexity_handler'
CATEGORY_STATE = 'category_handler'
AMOUNT = 1
TYPE = 'multiple'
DEFEAT_POINTS = 1
level_points = {'easy': 1, 'medium': 2, 'hard': 3}
for i in req_category['trivia_categories']:
  categories_dict[i['name']] = i['id']
#https://opentdb.com/api_category.php to get all category
#https://opentdb.com/api_config.php look for help

def victories(user, scores):
    if user in score:
        score[user]['victories'] += level_points[scores]
    else: 
        score[user] = {'victories': 0, 'defeats': 0}
        score[user]['victories'] += level_points[scores]

def defeats(user):
    if user in score:
        score[user]['defeats'] += DEFEAT_POINTS
    else: 
        score[user] = {'victories': 0, 'defeats': 0}
        score[user]['defeats'] += DEFEAT_POINTS

def menu(markup):
    kb1 = telebot.types.KeyboardButton('Question')
    kb2 = telebot.types.KeyboardButton('Level')
    kb3 = telebot.types.KeyboardButton('Category')
    kb4 = telebot.types.KeyboardButton('Score')
    kb5 = telebot.types.KeyboardButton('/start')
    markup.add(kb1, kb2, kb3, kb4, kb5)

def set_markup():
    return telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True, selective=True)


@bot.message_handler(func=lambda message:states.get(message.from_user.id, MAIN_STATE) == MAIN_STATE)
def main_handler(message):
  
    if message.from_user.id not in level:
        level[message.from_user.id] = 'easy'
    if message.from_user.id not in score:
        score[message.from_user.id] = {'victories': 0, 'defeats': 0}  
    if message.from_user.id not in category_id:
        category_id[message.from_user.id] = None
    if 'quest' in message.text.lower():
        response = requests.get(api_url, params={'amount': AMOUNT, 'category': category_id[message.from_user.id], 'difficulty': level[message.from_user.id], 'type': TYPE}).json()
        correct_answers[message.from_user.id] = html.unescape(response['results'][0]['correct_answer'])
        answers[message.from_user.id] = [html.unescape(response['results'][0]['correct_answer'])] + [html.unescape(i) for i in response['results'][0]['incorrect_answers']]
        random.shuffle(answers[message.from_user.id])
        random.shuffle(answers[message.from_user.id])
        question = str(html.unescape(response['results'][0]['question'])) + ': ' + '; '.join(answers[message.from_user.id])
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True, selective=True)
        buttons = []
        for answer in answers[message.from_user.id]:
            buttons.append(telebot.types.KeyboardButton(answer))
        markup.add(*buttons)
        bot.send_message(message.from_user.id, question, reply_markup=markup)
        states[message.from_user.id] = QUESTION_STATE
    elif message.text == '/start':
        markup = set_markup()
        menu(markup)
        bot.send_message(message.from_user.id, 'Hello, ' + message.from_user.first_name + '!')
        bot.send_message(message.from_user.id, 'It\'s a bot-game "Who Wants to Be a Millionaire?"')
        bot.send_message(message.from_user.id, 'I can ask interesting questions, change the level of difficulty, the category and show the score', reply_markup=markup)
        score[message.from_user.id] = {'victories': 0, 'defeats': 0}
        level[message.from_user.id] = 'easy'
        category_id[message.from_user.id] = None
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
        markup = set_markup()
        menu(markup)
        bot.send_message(message.from_user.id, 'victories: ' + str(score[message.from_user.id]['victories']) + ' / ' + 'defeats: '  + str(score[message.from_user.id]['defeats']), reply_markup=markup)
    elif 'category' in message.text.lower():
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True, selective=True)
        buttons = []
        for category in categories_dict.keys():
            buttons.append(telebot.types.KeyboardButton(category))
        markup.add(*buttons)
        bot.send_message(message.from_user.id, 'Choose a category:', reply_markup=markup)
        states[message.from_user.id] = CATEGORY_STATE
    else:
        bot.reply_to(message, "I don't understand you")

@bot.message_handler(func=lambda message:states.get(message.from_user.id, MAIN_STATE) == QUESTION_STATE)
def question(message):
    markup = set_markup()
    menu(markup)
    if message.text == correct_answers[message.from_user.id]:
        bot.send_message(message.from_user.id, "That's right!", reply_markup=markup)
        victories(message.from_user.id, level[message.from_user.id])
        states[message.from_user.id] = MAIN_STATE
    elif message.text in answers[message.from_user.id] and message.text != correct_answers[message.from_user.id]:
        bot.send_message(message.from_user.id, 'Wrong!:( Correct answer is ' + correct_answers[message.from_user.id], reply_markup=markup)
        defeats(message.from_user.id)
        states[message.from_user.id] = MAIN_STATE
    else:
        bot.reply_to(message, "I don't understand you")

@bot.message_handler(func=lambda message:states.get(message.from_user.id, MAIN_STATE) == COMPLEXITY_STATE)
def complexity(message):
    markup = set_markup()
    menu(markup)
    if message.text == 'easy':
        bot.send_message(message.from_user.id, 'OK! There will be easy questions:)', reply_markup=markup)
        level[message.from_user.id] = 'easy'
        states[message.from_user.id] = MAIN_STATE
    elif message.text == 'medium':
        bot.send_message(message.from_user.id, 'There will be questions of average complexity and double points for the victory!', reply_markup=markup)
        level[message.from_user.id] = 'medium'
        states[message.from_user.id] = MAIN_STATE
    elif message.text == 'hard':
        bot.send_message(message.from_user.id, 'There will be difficult questions and triple points for the victory!', reply_markup=markup)
        level[message.from_user.id] = 'hard'
        states[message.from_user.id] = MAIN_STATE
    else:
        bot.reply_to(message, "I don't understand you")


@bot.message_handler(func=lambda message:states.get(message.from_user.id, MAIN_STATE) == CATEGORY_STATE)
def category(message):
    markup = set_markup()
    menu(markup)
    try:
      category_id[message.from_user.id] = categories_dict[message.text]
      states[message.from_user.id] = MAIN_STATE
      bot.send_message(message.from_user.id, 'You have selected a category {}'.format(message.text), reply_markup=markup)
    except KeyError:
      bot.reply_to(message, "I don't understand you")
   
bot.polling()
