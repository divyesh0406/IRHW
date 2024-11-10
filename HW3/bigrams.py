import os
import re
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

target_bigrams = {
    "computer science",
    "information retrieval",
    "power politics",
    "los angeles",
    "bruce willis"
}

def preprocessing(text):
    text = re.sub(r'[^\w\s]', ' ', text)  
    text = re.sub(r'\d+', ' ', text)      
    return text.lower()                   

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        docID, content = first_line.split('\t', 1)  
        content = preprocessing(content)          
        words = content.split()                     
    return docID, words

def mapper(file_path):
    docID, words = read_file(file_path)
    bigram_count = defaultdict(int)
    
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        if bigram in target_bigrams:
            bigram_count[bigram] += 1
    
    return docID, bigram_count

def shuffler(mapped_data):
    shuffled = defaultdict(lambda: defaultdict(int))  
    for docID, bigram_count in mapped_data:
        for bigram, count in bigram_count.items():
            shuffled[bigram][docID] += count  
    return shuffled

def reducer(shuffled_data):
    reduced_output = []
    for bigram, doc_counts in shuffled_data.items():
        counts = ' '.join([f"{docID}: {count}" for docID, count in doc_counts.items()])
        reduced_output.append(f"{bigram} {counts}")
    return reduced_output

def main(folder):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.txt')]
    
    with ProcessPoolExecutor() as executor:
        mapped_data = list(executor.map(mapper, files))  
    
    shuffled_data = shuffler(mapped_data)
    
    final_output = reducer(shuffled_data)
    
    output_file = "HW3/out/selected_bigram_index22.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in final_output:
            f.write(line + "\n")
    
    print(f"Selected bigram counts written to {output_file}")

if __name__ == "__main__":
    folder = "HW3/data/devdata"  
    main(folder)
