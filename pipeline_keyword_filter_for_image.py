import luigi


class SourceData(luigi.Task):
    parameter = luigi.Parameter()

    def requires(self):
        return  # Mongo data

    def output(self):
        pass

    def run(self):
        pass


class ExtractText(luigi.Task):
    parameter = luigi.Parameter()

    def requires(self):
        return SourceDt(parameter=self.parameter)
        pass

    def output(self):
        pass

    def run(self):
        pass


class TranslateText(luigi.Task):
    parameter = luigi.Parameter()

    def requires(self):
        return ExtractText(parameter=self.parameter)
        pass

    def output(self):
        pass

    def run(self):
        pass


class SourceKeywords(luigi.Task):
    parameter = luigi.Parameter()

    def requires(self):
        return TranslateText(parameter=self.parameter)
        return  # Mongo data

    def output(self):
        pass

    def run(self):
        pass


class FilterText(luigi.Task):
    parameter = luigi.Parameter()

    def requires(self):
        return SourceKeywords(parameter=self.parameter)
        pass

    def output(self):
        pass

    def run(self):
        pass


class StoreLabel(luigi.Task):
    date = luigi.DataParameter()

    def requires(self):
        return FilterText(date=self.data)

    def output(self):
        pass

    def run(self):
        pass


class KeywordFilter(luigi.WrapperTask):
    date = luigi.DateParameter()

    def requires(self):
        return StoreLabel(date=self.date)
