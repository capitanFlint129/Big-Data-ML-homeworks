
from mrjob.job import MRJob
from mrjob.step import MRStep

class MRTask1(MRJob):
    def mapper_init(self):
        self.count = {}
    
    def mapper(self, _, line):
        row_id, row = line.split(' ', 1)
        row_id = row.split('"', 2)[1]
        if row_id != 'character':
            character_name = row.split('"', 2)[1]
            self.count.setdefault(character_name, 0)
            self.count[character_name] += 1

    def mapper_final(self):
        for character_name, phrases_count in self.count.items():
            yield character_name, phrases_count

    def reducer_init(self):
        self.final_count = {}
    
    def reducer(self, character_name, phrases_counts):
        yield None, (character_name, sum(phrases_counts))

    def reducer_all_data(self, _, final_count_pairs):
        final_count_pairs = sorted(
            final_count_pairs,
            reverse=True,
            key=lambda x: x[1]
        )[:20]
        for character_name, phrases_count in final_count_pairs:
            yield character_name, phrases_count
    
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
    MRTask1.run()
