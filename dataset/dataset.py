from metaflow import StepMutator, config_expr, current, user_step_decorator

DEPS = {"duckdb": "1.3.2", "pyarrow": "20.0.0"}

@user_step_decorator
def process_dataset(step_name, flow, inputs=None, attr=None):
    import duckdb

    sql = f"""SELECT * FROM '{attr["url"]}'"""
    fltr = attr.get("filter")
    if fltr:
        sql += f"WHERE {fltr}"
    con = duckdb.connect()
    print("🔄 Preparing data")
    flow.table = con.execute(sql).fetch_arrow_table()
    print("✅ Data prepared")
    yield
    del flow.table

class dataset(StepMutator):
    def init(self, *args, **kwargs):
        self.url = kwargs["url"]
        self.filter = kwargs.get("filter")

    def mutate(self, mutable_step):
        mutable_step.add_decorator(
            "pypi", deco_kwargs={"packages": DEPS}, duplicates=mutable_step.ERROR
        )
        mutable_step.add_decorator(
            process_dataset,
            deco_kwargs={"filter": self.filter, "url": self.url},
            duplicates=mutable_step.ERROR,
        )
