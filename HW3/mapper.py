from collections import defaultdict
import re

def preprocess(data):
    data = re.sub(r'[^\w\s]', '', data)
    return data.lower()

def read_file(filename):
    with open(filename, 'r', encoding = 'utf-8') as file:
        docs = file.readlines()
    return map_reduce(docs)

def map_reduce(docs):
    mapped_data = []
    for doc in docs: 
        mapped_data.extend(mapper(doc))
    shuffle_data = shuffler(mapped_data)

    return reducer(shuffle_data)

def mapper(mapping_data):
    word_count = defaultdict(int)
    mapping_data = preprocess(mapping_data)
    for word in mapping_data.split():
        word_count[word] +=1
    return word_count.items()

def shuffler(shuffling_data):
    shuffled_data = defaultdict(list)
    for word, count in shuffling_data:
        shuffled_data[word].append(count)
    return shuffled_data

def reducer(reduce_data):
    reduced_data = {}
    for word, count in reduce_data.items():
        reduced_data[word] = sum(count)
    return reduced_data
#
filename = 'HW3/sample.txt'
res = read_file(filename)
print(res)
