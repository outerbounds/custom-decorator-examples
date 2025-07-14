from metaflow import FlowSpec, step, resources, Config

from flow_linter import flow_linter

@flow_linter
class HungryFlow(FlowSpec):

    limits = Config('limits', default='limits.json')

    @resources(cpu=16)
    @step
    def start(self):
        self.next(self.end)

    @step
    def end(self):
        pass

if __name__ == '__main__':
    HungryFlow()
