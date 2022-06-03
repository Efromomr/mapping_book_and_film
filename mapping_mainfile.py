import re
import spacy
import math
from collections import Counter

nlp = spacy.load('en_core_web_sm')

script = ""

characters = []
film_dialogues = [] 
book_dialogues = []

def get_sentence(string, i):
    sent = ""
    while not (string[i] in ['.', "?", "!"] and string[i+2].isupper()):
        sent+= string[i]
        i-=1
    return sent[::-1], i
def counter_cosine_similarity(c1, c2):
    c1 = {item.lower() for item in c1}
    c2 = {item.lower() for item in c2}
    c1 = Counter(c1)
    c2 = Counter(c2)
    terms = set(c1).union(c2)
    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
    magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))
    if magA*magB == 0:
      return 0
    return (dotprod / (magA * magB) * 100)
film_dialogues = []
local_list = []
characters = []
with open('LordoftheRings1-FOTR (1).txt', 'r', encoding = 'utf-8') as file:
    speaking_dict = {"words":""}
    for line in file:
        if "CUT TO:" in line:
          film_dialogues.append(local_list)
          local_list = []
        elif re.match(r'^\s+([A-Z][A-Z]+[^:.])', line):
            speaking_dict = {"speaker": re.sub(r' (.*)', r'', line.strip()), "words": ""}
            characters.append(re.sub(r'\s?\(.*', r'', line.strip()))
            
        elif re.match(r' {10}([^\n]+)\n', line) and speaking_dict['speaker']:
            speaking_dict['words']+=line.strip() + " "
        elif not line.strip() and speaking_dict['words']:
          local_list.append(speaking_dict)
          speaking_dict = {'speaker': '', 'words':''}
all_stopwords = nlp.Defaults.stop_words
characters = set(characters)

book_dialogues = []
with open("Chak_Palanik__Fight_Club.txt") as book:
    book_text = book.read()
    phrases = re.finditer(r'(?<=[‘\'])([\w](?:(?![,!.?][\'’]).)+)[,!.?][\'’]([^\.\'’‘\n]+[\.,;])?', book_text, re.MULTILINE)
    for phrase in phrases:
        no_subj = True
        speaking_dict = {"words": phrase.group(1), "place": phrase.span()}
        if phrase.group(2):
            doc = nlp(phrase.group(2))
            for token in doc:
                if token.dep_ == "nsubj" and token.text.upper() in characters and token.head.dep_ == "ROOT":
                    no_subj = False
                    speaking_dict['speaker'] = token.text
        previous_sentence, counter = get_sentence(book_text, phrase.span()[0]-1)
        depth = 0
        while no_subj and depth < 3:
            doc = nlp(re.sub(r'[‘\'][^\.\'’‘\n]+[\.,;]', '', previous_sentence))
            for token in doc:
                if token.dep_ == "nsubj" and token.text.upper() in characters and token.head.dep_ == "ROOT":
                    no_subj = False
                    speaking_dict['speaker'] = token.text
            previous_sentence, counter = get_sentence(book_text, counter-1)
            depth+=1
        book_dialogues.append(speaking_dict)


characters_book = []
for i in range(book_text.count('\n')):
  characters_book.append([])
with open("LOTR_book.txt", encoding="windows-1252") as book:
  book_lines = book.readlines()
  chars_dict = {key.lower(): 0 for key in characters}
  for dialogue in book_dialogues:
    if 'speaker' in dialogue:
      for i in range(25):
        characters_book[min(book_text[:dialogue['place'][0]].count("\n") + i, 7162)].append(dialogue["speaker"])

for num, value in enumerate(characters_book):
  characters_book[num] = set(value)

linked_scenes = []
book_text = ''
with open("LOTR_book.txt", encoding="windows-1252") as book:
  book_text = book.read()
book_parts = [book_text.lower()]
book_lines = book_text.split('\n')
for scene in film_dialogues:
  scene_included = False
  for dialogue in scene:
    if scene_included:
      break
    for sent in re.split(r'[.?!] (?=[A-Z])', dialogue['words']):
      sent_tokens = [word.lower() for word in sent.split() if not word.lower() in all_stopwords]
      if book_parts[-1].count(sent.lower()) == 1 and len(sent_tokens)>1:
        print(sent)
        scene_included = True
        lists_similarity = counter_cosine_similarity([dial['speaker'] for dial in scene], characters_book[book_text[:book_text.lower().find(sent.lower())].count('\n')])
        same_scene = True
        string = book_lines[book_text[:book_text.lower().find(sent.lower())].count('\n')]
        i = 0
        while same_scene and book_text[:book_text.lower().find(sent.lower())].count('\n')+i < 7163 and int(counter_cosine_similarity([dial['speaker'] for dial in scene], characters_book[book_text[:book_text.lower().find(sent.lower())].count('\n')+i]) != 0):
          if counter_cosine_similarity([dial['speaker'] for dial in scene], characters_book[book_text[:book_text.lower().find(sent.lower())].count('\n')+i]) < lists_similarity:
            same_scene = False
            
          else:
            string += book_lines[book_text[:book_text.lower().find(sent.lower())].count('\n')+i]
            i+=1
            
        same_scene = True
        i = -1
        while same_scene and book_text[:book_text.lower().find(sent.lower())].count('\n')+i > 0 and int(counter_cosine_similarity([dial['speaker'] for dial in scene], characters_book[book_text[:book_text.lower().find(sent.lower())].count('\n')+i]) != 0):
          if counter_cosine_similarity([dial['speaker'] for dial in scene], characters_book[book_text[:book_text.lower().find(sent.lower())].count('\n')+i]) < lists_similarity:
            same_scene = False
          else:
    
            string = book_lines[book_text[:book_text.lower().find(sent.lower())].count('\n')+i] + string
            i-=1
        linked_scenes.append([scene, string])

with open("output.txt", 'w') as file:
  for scene in linked_scenes:
    for dial in scene[0]:
      file.write(str(dial) + "\n")
    file.write(str(scene[1] + '\n'))
