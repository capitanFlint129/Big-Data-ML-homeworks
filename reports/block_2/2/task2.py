
from mrjob.job import MRJob
from mrjob.step import MRStep

class MRTask2(MRJob):
    def mapper_init(self):
        self.longest_phrase = {}
    
    def mapper(self, _, line):
        row_id, row = line.split(' ', 1)
        row_id = row_id.split('"', 2)[1]
        if row_id != 'character':
            _, character_name, phrase  = row.split('"', 2)
            phrase = phrase[2:-1]
            self.longest_phrase.setdefault(character_name, "")
            if len(self.longest_phrase[character_name])  < len(phrase):
                self.longest_phrase[character_name] = phrase

    def mapper_final(self):
        for character_name, longest_phrase in self.longest_phrase.items():
            yield character_name, longest_phrase

    def reducer_init(self):
        self.longest_phrases = {}
    
    def reducer(self, character_name, phrases):
        best = ""
        for phrase in phrases:
            if len(phrase) > len(best):
                best = phrase
        yield None, (character_name, best)

    def reducer_all_data(self, _, final_pairs):
        final_pairs = sorted(
            final_pairs,
            reverse=True,
            key=lambda x: len(x[1])
        )
        for character_name, phrase in final_pairs:
            yield character_name, phrase
    
    def steps(self):
        return [
            MRStep(
                mapper_init=self.mapper_init,
                mapper=self.mapper,
                mapper_final=self.mapper_final,
                reducer_init=self.reducer_init,
                reducer=self.reducer,
            ),
            MRStep(reducer=self.reducer_all_data)
        ]
            
        
if __name__ == "__main__":
    MRTask2.run()
