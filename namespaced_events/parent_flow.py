from metaflow import FlowSpec, step, project, Config
from namespaced_trigger import namespaced_trigger


@project(name="foo")
class HelloFlowUpstream(FlowSpec):

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
        namespaced_trigger.raise_event("food", safe_publish=True)


if __name__ == "__main__":
    HelloFlowUpstream()
