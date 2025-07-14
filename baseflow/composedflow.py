import math
from baseflow import BaseFlow
from metaflow import step, Config, current, resources

from dataset import dataset

class ComposedFlow(BaseFlow):

    data_config = Config('dataset', default='dataset.json')

    @resources(cpu=2)
    @dataset(url=data_config.url)
    @step
    def start(self):
        print(f"Project {current.project_name}")
        print("Number of rows:", self.number_of_rows())
        self.next(self.end)

    @step
    def end(self):
        pass

if __name__ == '__main__':
    ComposedFlow()
