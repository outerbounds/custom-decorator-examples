from metaflow import FlowMutator
from fallback import fallback

class robust_flow(FlowMutator):
    def init(self, *args, **kwargs):
        self.disable_fallback = bool(kwargs.get("disable_fallback"))
        self.fallback_attributes = {}
        fallback_indicator = kwargs.get("fallback_indicator")
        if fallback_indicator:
            self.fallback_attributes["indicator"] = fallback_indicator

    def mutate(self, mutable_flow):
        for step_name, step in mutable_flow.steps:
            step.add_decorator("retry", duplicates=step.IGNORE)
            if not self.disable_fallback:
                step.add_decorator(
                    fallback,
                    deco_kwargs=self.fallback_attributes,
                    duplicates=step.IGNORE
                )

