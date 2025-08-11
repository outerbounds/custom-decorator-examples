from metaflow import FlowMutator
import sys
import re


class namespaced_trigger(FlowMutator):
    """
    A flow decorator that creates namespaced event triggers for Metaflow flows.

    This decorator automatically formats event names with project and branch information,
    enabling namespaced event-driven workflows. It requires either an `event` or `events`
    parameter and works in conjunction with Metaflow's Config system.

    Args:
        event (str, optional): Single event name to trigger on
        events (list, optional): List of event names to trigger on
        options (dict, optional): Additional trigger options
        config_name (str, optional): Name of Config object to use. Defaults to "project"
        show_warnings (bool, optional): Whether to show warnings. Defaults to True

    Required Setup:
        - Flow must have a Config object (default name: "project")
        - Flow should use @project decorator for project name or provide the "name" in the config.
        - The values provided in the config will override the values in the @project decorator except for the name.
        - Branches can only be overridden in the config. If users provide branches via `--branch` or `--production` then they wont be picked up.
        - Config can specify branch and production settings

    Event Name Format:
        Events are automatically namespaced as: {project_name}.{branch}.{event_name}
        - Branch format: "prod.{branch}" (production) or "test.{branch}" (non-production)
        - For user branches: "user.{username}" when no branch specified

    Example:

        Upstream Flow:

        ```python
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

        ```

        Downstream Flow:

        ```python
        from metaflow import FlowSpec, step, project, Config
        from namespaced_trigger import namespaced_trigger

        @namespaced_trigger(event="food")
        @project(name="foo")
        class HelloFlowDownstream(FlowSpec):
            project = Config("project", default_value={})

            @step
            def start(self):
                print("Triggered by namespaced event!")
                self.next(self.end)

            @step
            def end(self):
                pass
        ```

        Deploy the upstream flow with the correct project values like:
        ```bash
        python upstream_flow.py --branch bar --production argo-workflows create
        ```
        Deploy the Downstream flow with the config values like:
        ```bash
        python downstream_flow.py --config-value project '{"branch": "bar", "production": true}' argo-workflows create
        ```

        Triggering the upstream flow like:
        ```bash
        python upstream_flow.py --branch bar --production argo-workflows trigger
        ```

    Publishing Events from Upstream Flows:
        Ensure that the project decorator is set with the correct project/branch/production values.
        Use the class method to publish events from upstream flows:
        ```python
        namespaced_trigger.raise_event("food", safe_publish=True)
        ```


    Note:
        Cannot be used together with @trigger decorator on the same flow.
    """

    def init(self, *args, **kwargs):
        self.event = kwargs.get("event", None)
        self.events = kwargs.get("events", [])
        self.options = kwargs.get("options", {})

        self.config_name = kwargs.get("config_name", "project")

        self._show_warnings = kwargs.get("show_warnings", True)

        if len(self.events) == 0 and not self.event:
            raise Exception(
                "@namespaced_trigger requires `event` or `events` arguement"
            )

    @classmethod
    def raise_event(cls, event_name, payload=None, safe_publish=False):
        from metaflow import current
        from metaflow.integrations import ArgoEvent

        if "project_flow_name" in current:
            event_name = ".".join(
                current.project_flow_name.split(".")[:-1] + [event_name]
            )
            event_name = re.sub(r"[^a-zA-Z0-9_\-\.]", "", event_name)

        if safe_publish:
            ArgoEvent(name=event_name).safe_publish(
                payload=payload,
            )
        else:
            ArgoEvent(name=event_name).publish(
                payload=payload,
            )

    @staticmethod
    def _format_event_name(
        project_name, given_branch, deploy_prod, user_name, event_name
    ):
        if given_branch:
            if deploy_prod:
                branch = "prod.%s" % given_branch
            else:
                branch = "test.%s" % given_branch
        elif deploy_prod:
            branch = "prod"
        else:
            branch = "user.%s" % re.sub(r"[^a-zA-Z0-9_\-\.]", "", user_name)
        return ".".join((project_name, branch, event_name))

    def _warn(self, message):
        if self._show_warnings:
            print(message, file=sys.stderr)

    def pre_mutate(self, mutable_flow):
        from metaflow.util import get_username
        from metaflow import trigger, project

        config_obj = {}
        for config_name, config_value in mutable_flow.configs:
            if config_name == self.config_name:
                config_obj = config_value
                break
        else:
            self._warn("No config object found for %s" % self.config_name)

        project_branch = config_obj.get("branch", None)
        is_production = config_obj.get("production", False)

        def _extract_project_decorator():
            for name, qual_name, args, kwargs in mutable_flow.decorator_specs:
                if name == "project":
                    return kwargs
            return None

        def _extract_trigger():
            for name, qual_name, args, kwargs in mutable_flow.decorator_specs:
                if name == "trigger":
                    return kwargs
            return None

        def _add_event_kwargs(_evt_kwargs):
            mutable_flow.add_decorator(deco_type=trigger, deco_kwargs=_evt_kwargs)

        def _override_project_decorator(_project_kwargs):
            mutable_flow.add_decorator(
                deco_type=project,
                deco_kwargs=_project_kwargs,
                duplicates=3,  # MutableFlow.OVERRIDE,
            )

        if _extract_trigger():
            raise Exception(
                "You cannot set both @trigger or @namespaced_trigger on the same Flow. Please use on or the other."
            )

        project_kwargs = _extract_project_decorator()
        if project_kwargs is None:
            _add_event_kwargs(
                dict(event=self.event, events=self.events, options=self.options)
            )
            return

        project_name = project_kwargs.get("name", config_obj.get("name", None))

        if project_name is None:
            raise Exception(
                "You must set a project name in the @project decorator or in the %s config"
                % self.config_name
            )

        _override_project_decorator(
            dict(
                name=project_name,
                branch=project_branch,
                production=is_production,
            )
        )

        _add_event_kwargs(
            dict(
                event=(
                    None
                    if self.event is None
                    else self._format_event_name(
                        project_name=project_name,
                        given_branch=project_branch,
                        deploy_prod=is_production,
                        user_name=get_username(),
                        event_name=self.event,
                    )
                ),
                events=[
                    self._format_event_name(
                        project_name=project_name,
                        given_branch=project_branch,
                        deploy_prod=is_production,
                        user_name=get_username(),
                        event_name=e,
                    )
                    for e in self.events
                ],
                options=self.options,
            )
        )
