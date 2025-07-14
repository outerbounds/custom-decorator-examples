from metaflow import FlowSpec, step, resources, Config

from dataset import dataset

class DatasetFlow(FlowSpec):

    data_config = Config('dataset', default='dataset.json')

    @dataset(url=data_config.url, filter=data_config.filter)
    @step
    def start(self):
        print(self.table)
        self.next(self.end)

    @step
    def end(self):
        pass

if __name__ == '__main__':
    DatasetFlow()


