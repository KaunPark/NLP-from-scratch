# -*- coding: utf-8 -*-
"""
web data resit assignment.
@Kaun Park
You should install nltk, SpaCy, Beautifulsoup, and wikipedia to run.
!pip install nltk spacy wikipedia

"""

import nltk
import spacy
import wikipedia
import requests
from bs4 import BeautifulSoup
import string
import pandas as pd
import re
import gzip

nltk.download('punkt')

nlp = spacy.load('en_core_web_sm')
KEYNAME = "WARC-TREC-ID"
non_relevant_html_tags = ['script', 'style', 'header', 'noscript', 'link', 'footer', 'aside class']

def find_entities(payload):  #From starter_code
    if payload == '':
        return
    key = None
    for line in payload.splitlines():
        if line.startswith(KEYNAME):
            key = line.split(':')[1]
            break
            
    kb_data = BeautifulSoup(payload, 'html.parser') 
    
    for tag in kb_data(non_relevant_html_tags): #Extract non relevant tags 
        tag.extract()
    
    text_raw = ""
    
    for data in kb_data.find_all("p"):
        text_raw = text_raw + data.get_text()
        
    text = text_raw.strip("\n").replace("\n", " ").replace("\r", " ") 
    
    doc = nlp(text) #Return object containing all components and data needed to process text
    
    ent_dict = dict() #dict() for duplicate free
    included_lables = ['PERSON', "ORG", "GPE"] #Limited to 3 NE for accuracy
    for ent in doc.ents: 
        if (ent.label_  in included_lables) and (ent.text not in ent_dict.keys()):
            new_ent_text = re.sub(r'[!@#$%^&*(){};:,/<>?\|`~"+_"]', '', ent.text)
            ent_dict.update({new_ent_text: ent.label_}) #update the dict
      
    for ent, label in ent_dict.items(): #From starter_code
        if key and (ent in payload):
            yield key, ent, label

ent_dict_total =dict()

def split_records(stream): #From starter_code
    payload = ''
    for line in stream:
        if line.strip() == "WARC/1.0":
            yield payload
            payload = ''
        else:
            payload += line
    yield payload

ents = []
ent_total = dict()
if __name__ == '__main__':
    import sys
    try:
        _ = sys.argv
        INPUT = 'sample.warc.gz'
    except Exception as e:
        
        print('Usage: python3 starter-code.py INPUT')
        sys.exit(0)

    with gzip.open(INPUT, 'rt', errors = 'ignore') as fo:
        for record in split_records(fo):
            entities = find_entities(record)
            for key, ent, label in entities:
                ents.append(ent)
                ent_total[ent]= [key, label]

    for ent in ent_total.keys():
      key, label = ent_total[ent]
      print("Entity: " + key + '\t'+ ent + '\t' + label) #KEYNAME, entity, label

WIKIPEDIA_URL = 'https://en.wikipedia.org/wiki/'

def scrape_web_page(web_page):
    requested_page = requests.get(web_page) #extract the page content
    wiki_data = BeautifulSoup(requested_page.text, 'html.parser') #html version of the website
    link_list = [link.get('href') for link in wiki_data.find_all('a')]
    text_par = [paragraph.get_text() for paragraph in wiki_data.select('p')] #Return the text from each paragraph from the webpage
    result = ("('%s)" % "','".join(text_par)) # Making a list into a string with .join()

    # remove unnecessary punction and white spaces
    for character in string.punctuation:
        result = result.replace(character, '')
    return result

def get_related_entities(option):
  # get entities related to option
  try:
    page = scrape_web_page(f'{WIKIPEDIA_URL}{option}')
    # Use SpaCy to do NER on each sentence
    doc = nlp(page)
    entities = []
    for ent in doc.ents:
        if ent.label_ in ('PERSON', "ORG", "GPE"): #to get the three simple ner
            entities.append(ent.text) #should include capital letters
  except:
    pass

def link_entities(entities):

# For each named entity, look up the corresponding wikipedia page and rank candidates
  
    candidate_entities = []
    for entity in entities:
        try: 
            options = wikipedia.search(entity)
            candidate_entities.append({entity: options})
        except:
            pass

    print('candidate_entities: ',candidate_entities)
    #Ranking-vectorization comparison
    
    linked_entities = {}
    for options in candidate_entities:
      options_with_related_entities = {}
      for option in options:
        options_with_related_entities[option] = get_related_entities(option)
      
      option_with_score = {}
      for option in options_with_related_entities.keys():
          print(options_with_related_entities)
          score = len(set(options_with_related_entities[option]) & set(entities)) / len(entities)
          option_with_score[option] = score
      linked_entities[max(option_with_score)] = f'{WIKIPEDIA_URL}{option}'.replace(' ', '_')

    return linked_entities

linked_entities = link_entities(ent_total.keys()) # should be the input

total_linked_entities = dict(ent_total)

for ent in linked_entities.keys():
	key, org = total_linked_entities[ent] #entity name is key
	link = linked_entities[ent]
total_linked_entities[ent] = [key, org, link]
for ent in linked_entities.keys():
	key, org, link = total_linked_entities[ent]
	print(f"ENTITY: {key}<TAB>{ent}<TAB>{link}")
