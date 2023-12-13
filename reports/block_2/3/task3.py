
from collections import defaultdict

import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords

from mrjob.job import MRJob
from mrjob.step import MRStep


def process_phrase(phrase):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = sent_detector.tokenize(phrase.strip())

    tokenizer = RegexpTokenizer(r"[\w|-|']+")
    sentences = [tokenizer.tokenize(sentence) for sentence in sentences]

    stop_words = set(stopwords.words('english'))

    lemmatizer = WordNetLemmatizer()
    sentences = [
        [
            lemmatizer.lemmatize(word.lower()) for word in sentence if word not in stop_words
        ] for sentence in sentences
    ]
    return sentences

class MRTask3(MRJob):
    def mapper_init(self):
        self.count_bigrams = defaultdict(lambda : 0)
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
    
    def mapper(self, _, line):
        row_id, row = line.split(' ', 1)
        row_id = row_id.split('"', 2)[1]
        if row_id != 'character':
            _, character_name, phrase  = row.split('"', 2)
            processed_sentences = process_phrase(phrase[2:-1])
            for sentence in processed_sentences:
                for i in range(len(sentence) - 1):
                    bigram = (sentence[i], sentence[i + 1])
                    self.count_bigrams[bigram] += 1

    def mapper_final(self):
        for bigram, count in self.count_bigrams.items():
            yield bigram, count

    def reducer_init(self):
        self.frequent_bigrams = {}
    
    def reducer(self, bigram, counts):
        bigram = (bigram[0], bigram[1])
        self.frequent_bigrams[bigram] = sum(counts)

    def reducer_final(self):
        final_count_pairs = sorted(
            [(k, v) for k, v in self.frequent_bigrams.items()],
            reverse=True,
            key=lambda x: x[1]
        )[:20]
        for bigram, count in final_count_pairs:
            yield None, (bigram, count)

    def reducer_all_data(self, _, final_pairs):
        final_pairs = sorted(
            final_pairs,
            reverse=True,
            key=lambda x: x[1]
        )[:20]
        for bigram, count in final_pairs:
            yield bigram, count
    
    def steps(self):
        return [
            MRStep(
                mapper_init=self.mapper_init,
                mapper=self.mapper,
                mapper_final=self.mapper_final,
                reducer_init=self.reducer_init,
                reducer=self.reducer,
                reducer_final=self.reducer_final,
            ),
            MRStep(reducer=self.reducer_all_data)
        ]
            
        
if __name__ == "__main__":
    MRTask3.run()
