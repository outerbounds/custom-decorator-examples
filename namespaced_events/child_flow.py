from metaflow import FlowSpec, step, project, Config
from namespaced_trigger import namespaced_trigger


@namespaced_trigger(event="food")
@project(name="foo")
class HelloFlowDownstream(FlowSpec):

    project = Config(
        "project",
        default_value={},
    )

    @step
    def start(self):
        print("Hello World!")
        self.next(self.end)

    @step
    def end(self):
        print("Flow complete!")


if __name__ == "__main__":
    HelloFlowDownstream()
