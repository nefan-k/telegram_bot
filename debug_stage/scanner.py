import requests

with open("themes.txt", "w") as out:
  for i in range(34):
    req = requests.get('https://opentdb.com/api.php', params={'amount': 1, 'category': i, 'difficulty': 'easy', 'type': 'multiple'}).json()
    try:
      out.write(str(i) + " -- " + req['results'][0]['category'] + "\n")
    except IndexError:
      continue
  

  #req2 = requests.get('https://opentdb.com/api.php', params={'amount': 1, 'category': None, 'difficulty': None, 'type': 'multiple'}).json()
  #print(req2)
