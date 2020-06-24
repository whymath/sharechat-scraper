import luigi 
import pandas as pd

def test():
    print("test")


class SourceData(luigi.Task):
    filename = luigi.Parameter() # replace with date

    def output(self):
        print("hello")
        return luigi.LocalTarget("urls.csv") 

    def run(self):
        df = pd.read_csv(self.filename) 
        # replace with coll = os.system("mongo_access_script.py")
        # filter & load data to df using date parameter
        urls = df["s3_url"] 
        with self.output().open('w') as f:
            for url in urls:
                f.write(url)

class ExtractText(luigi.Task):
    filename = luigi.Parameter()

    def requires(self):
        return SourceData(filename=self.filename)

    def output(self):
        print('hello2')
        return luigi.LocalTarget("see.txt")

    def run(self):
        # os.system("text_extraction_script.py")
        print("1")
        with self.output().open('w') as f:
            f.write("let's see if this works")