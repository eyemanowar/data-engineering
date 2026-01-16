#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]


@click.command()
@click.option('--year', default=2021, type=int)
@click.option('--month', default=1, type=int)
@click.option('--pg_user', default='root', type=str)
@click.option('--pg_password', default='root', type=str)
@click.option('--pg_host', default='localhost', type=str)
@click.option('--pg_db', default='ny_taxi', type=str)
@click.option('--pg_port', default='5432', type=str)
@click.option('--target_table', default='yellow_taxi_data', type=str)
@click.option('--chunksize', default=100000, type=int)
def run(year, month, pg_user, pg_password, pg_host, pg_db, pg_port, target_table, chunksize):
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    url = f'{prefix}yellow_tripdata_{year}-{month:02d}.csv.gz'
    engine = create_engine(f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')
    
    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize,
    )

    first=True
    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine, 
                if_exists='replace'
                )
            first=False
            
        df_chunk.to_sql(
            name=target_table, 
            con=engine, 
            if_exists='append',
            )
        print(len(df_chunk))

    print("Ingestion completed")

if __name__ == '__main__':
    run()