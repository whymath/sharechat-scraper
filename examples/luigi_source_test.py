import luigi 
import pandas as pd


class SourceData(luigi.Task):
    filename = luigi.Parameter() # replace with date

    def output(self):
        return luigi.LocalTarget("urls.csv") 

    def run(self):
        df = pd.read_csv(self.filename) 
        # replace with coll = os.system("mongo_access_script.py")
        # filter & load data to df using date parameter
        urls = df["s3_url"] 
        with self.output().open('w') as f:
            for url in url:
                f.write(url)

class ExtractText(luigi.Task):
    filename = luigi.Parameter()

    def requires(self):
        return SourceData(filename=self.filename)

    def output(self):
        return luigi.LocalTarget("see.txt")

    def run(self):
        # os.system("text_extraction_script.py")
        with self.output().open('w') as f:
            f.write("let's see if this works")