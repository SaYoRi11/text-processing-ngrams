import csv, string
from collections import Counter
import nltk
from nltk.corpus import stopwords

with open('states.csv', 'r') as file:
    statesRows = []
    for line in file:
        row = line.split('   ')
        statesRows.append(row)

def makeObject(i): 
    object = {'State': state[i], 'Postal Abbr.': state[i+1], 'FIPS Code': state[i+2].replace('\n', '')}
    return object

jsonData = []
for state in statesRows:
    jsonData.append(makeObject(0))
    if len(state) > 3:
        jsonData.append(makeObject(3))

states = [s['State'].lstrip() for s in jsonData]

with open('notes.csv', 'r') as file:
    data = []
    for line in file:
        fields = line.split(',')
        data.append(fields)
        
        
notes = [d[5].split('--')[0].strip() for d in data][1:]

def remove_punctuation(text):
    if(type(text)==float):
        return text
    ans=""  
    for i in text:     
        if i not in string.punctuation:
            ans+=i    
    return ans

def generate_N_grams(text,ngram=1):
    text = remove_punctuation(text)
    words=[word for word in text.split(" ") if word not in set(stopwords.words('english'))]  
    temp=zip(*[words[i:] for i in range(0,ngram)])
    ans=[' '.join(ngram) for ngram in temp]
    return ans

def flatten(arr):
    return [item for sublist in arr for item in sublist]

unigrams = [generate_N_grams(n) for n in notes]
flat_uni = flatten(unigrams)

bigrams = [generate_N_grams(n, 2) for n in notes]
flat_bi = flatten(bigrams)

trigrams = [generate_N_grams(n, 3) for n in notes]
flat_tri = flatten(trigrams)

def get_top(flat):
    count_unigrams = Counter(flat)
    sorted_count = sorted(count_unigrams.items(), key = lambda x:x[1], reverse=True)
    return sorted_count[:30]

def get_state(note):
    states_set = set(states)
    tri_set = set(generate_N_grams(note, 3))
    if tri_set.intersection(states_set):
        return list(tri_set.intersection(states_set))[0]
    bi_set = set(generate_N_grams(note, 2))
    if bi_set.intersection(states_set):
        return list(bi_set.intersection(states_set))[0]
    uni_set = set(generate_N_grams(note))
    if uni_set.intersection(states_set):
        return list(uni_set.intersection(states_set))[0]

def filterSimilar(tags):
    final = []
    for s in tags:
        if not any([s in r for r in tags if s != r]):
            final.append(s)
    return final

def tag_note(note):
    top_bi = set([i[0] for i in get_top(flat_bi)])
    top_tri = set([i[0] for i in get_top(flat_tri)])
    tri_set = set(generate_N_grams(note, 3))
    bi_set = set(generate_N_grams(note, 2))
    tags = list(tri_set.intersection(top_tri)) + list(bi_set.intersection(top_bi))
    list(tri_set.intersection(top_tri))
    return filterSimilar(tags)

tags = [', '.join(tag_note(note)) for note in notes]
states = [get_state(note) for note in notes]

with open('result.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Note', 'Tags', 'State'])
    writer.writerows(list(zip(notes, tags, states)))