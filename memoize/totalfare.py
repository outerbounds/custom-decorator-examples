from metaflow import FlowSpec, step, Parameter, pypi

from memoize import memoize

URL = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2020-01.parquet'

class ComputeTotalFare(FlowSpec):

    reset = Parameter('reset', default=False, is_flag=True)
    url = Parameter('url', default=URL)

    @step
    def start(self):
        self.next(self.compute_fare)

    @memoize(artifact='total_fare', reset='reset')
    @pypi(packages={'duckdb': '1.3.2'})
    @step
    def compute_fare(self):
        import duckdb
        SQL = f"SELECT SUM(fare_amount) AS total_fare FROM '{self.url}'"
        self.total_fare = duckdb.query(SQL).fetchone()[0]
        self.next(self.end)

    @step
    def end(self):
        print(f"Total taxi fares: ${self.total_fare}")

if __name__ == '__main__':
    ComputeTotalFare()
