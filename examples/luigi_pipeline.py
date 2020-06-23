import luigi
"""
Notes
1. successfull creation of output files is required for luigi to consider a task complete
https://luigi.readthedocs.io/en/stable/api/luigi.task.html?highlight=complete#luigi.task.Task.complete

2. looks like parameters can't have names with underscore? i got an error when my parameter was 'string_param'

3. I've tested the following commands to pass parameters to the pipeline
 PYTHONPATH=. luigi --module luigi_pipeline KeywordFilter --string hello --local-scheduler
 PYTHONPATH=. luigi --module luigi_pipeline KeywordFilter --string hello --integer 42 --local-scheduler
 PYTHONPATH=. luigi --module luigi_pipeline KeywordFilter --string hello --integer 42 --float 23.3 --datehourparam 2013-07-10T19 --local-scheduler

4. luigi looks at output files to determine where to resume the failed tasks?! 
    that might mean clean up is important

5. A lot more parameter types are well documented here
https://luigi.readthedocs.io/en/stable/_modules/luigi/parameter.html#Parameter
"""


class SourceData(luigi.Task):
    string = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(
            'luigi_pipeline_output/source_data_output.txt')

    def run(self):
        print('runninng Source data')
        file = open('luigi_pipeline_output/source_data_output.txt', "w")
        file.write("test 1")
        file.close()


class ProcessData(luigi.Task):
    string = luigi.Parameter()

    def requires(self):
        return SourceData(string=self.string)

    def output(self):
        return luigi.LocalTarget(
            'luigi_pipeline_output/process_data_output.txt')

    def run(self):
        print('runninng process data')
        print('string param {}'.format(self.string))
        file = open('luigi_pipeline_output/process_data_output.txt', "w")
        file.write("test 2")
        file.close()


class SaveResult(luigi.Task):
    string = luigi.Parameter()
    integer = luigi.IntParameter()
    float = luigi.FloatParameter()
    datehourparam = luigi.DateHourParameter()

    def requires(self):
        return ProcessData(string=self.string)

    def output(self):
        return luigi.LocalTarget('luigi_pipeline_output/save_result.txt')

    def run(self):
        print('running save result')
        print('----printing all parameters in Save Result----')
        print('string_param {}'.format(self.string))
        print('integer param {}'.format(self.integer))
        print('float param {}'.format(self.float))
        print('date_hour_param {}'.format(self.datehourparam))
        print('----------------------------------------------')

        file = open('luigi_pipeline_output/save_result.txt', "w")
        file.write("test 3")
        file.close()


class KeywordFilter(luigi.WrapperTask):
    string = luigi.Parameter()
    integer = luigi.IntParameter()
    float = luigi.FloatParameter()
    datehourparam = luigi.DateHourParameter()

    def requires(self):
        return SaveResult(string=self.string,
                          integer=self.integer,
                          float=self.float,
                          datehourparam=self.datehourparam)
