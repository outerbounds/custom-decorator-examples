from metaflow import FlowMutator, config_expr, current


class flow_linter(FlowMutator):
    def mutate(self, mutable_flow):
        limits = mutable_flow.limits
        for step_name, step in mutable_flow.steps:
            for deco_name, _module, _args, attributes in step.decorator_specs:
                if deco_name in ("kubernetes", "batch", "resources"):
                    for key, limit in limits.items():
                        val = attributes.get(key)
                        if val and float(val) > limit:
                            print(
                                f"⚠️  Step[{step_name}] @{deco_name}({key}={val}) "
                                f"is higher than the limit of {limit} - fixed"
                            )
                            attributes[key] = limit
                            step.add_decorator(
                                deco_name,
                                deco_kwargs=attributes,
                                duplicates=step.OVERRIDE,
                            )
