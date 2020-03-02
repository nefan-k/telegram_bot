import requests
import random
import html
num_of_questions = 5
difficulty = 'easy'
letters = ['A','B','C','D']

req = requests.get('https://opentdb.com/api.php', params={'amount': num_of_questions, 'category': 15, 

'difficulty': difficulty, 'type': 'multiple'}).json()

answers_dict = {}
d = {}

for i in range(num_of_questions):
  answers = [html.unescape(j) for j in ([req['results'][i]['correct_answer']] + req['results'][i]

['incorrect_answers'])]
  for j in range(5):
    random.shuffle(answers)
  for j in letters:
    answers_dict[j] = answers[letters.index(j)]
  d[i] = answers_dict.copy()
  print(str(i + 1) + '). ' + html.unescape(req['results'][i]['question']))
  for key in letters:
    print(key + ': ' + answers_dict[key])
  print()

print('\n\n\nAnswers:\n')

for i in range(num_of_questions):
  for let in d[i].keys():
    if d[i][let] == req['results'][i]['correct_answer']:
        print(i + 1, '-', let)
        break
