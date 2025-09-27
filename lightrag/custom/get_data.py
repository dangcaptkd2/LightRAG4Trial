import os
import time

import dotenv
import pandas as pd
import psycopg2

dotenv.load_dotenv()


# PostgreSQL connection parameters
pg_conn_params = {
    "host": os.getenv("SQL_HOST"),
    "port": os.getenv("SQL_PORT"),
    "dbname": os.getenv("SQL_DATABASE_AACT"),
    "user": os.getenv("SQL_USERNAME"),
    "password": os.getenv("SQL_PASSWORD"),
}


def get_total_trials():
    """Get the total number of trials in the studies table."""
    conn = psycopg2.connect(**pg_conn_params, connect_timeout=300)  # type: ignore
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ctgov.studies")
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total


def get_nct_with_eligibility_criteria(list_nct_ids):
    """Fetch a batch of trials from PostgreSQL using keyset pagination."""
    conn = psycopg2.connect(**pg_conn_params, connect_timeout=300)  # type: ignore
    cursor = conn.cursor()
    # Ensure we pass a native Python list of strings for psycopg2 adaptation
    if not isinstance(list_nct_ids, (list, tuple)):
        try:
            list_nct_ids = list(list_nct_ids)
        except TypeError:
            list_nct_ids = [list_nct_ids]
    list_nct_ids = [str(x) for x in list_nct_ids]
    query = """
    SELECT
        s.nct_id,
        e.criteria AS eligibility_criteria
    FROM
        ctgov.studies s
    LEFT JOIN
        ctgov.eligibilities e ON s.nct_id = e.nct_id
    WHERE
        s.nct_id = ANY(%s);
    """

    # Use an empty string or a very low value for the first batch
    cursor.execute(query, (list_nct_ids,))
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()

    # Return the rows, column names, and the last nct_id for the next batch
    next_nct_id = rows[-1][0] if rows else None
    return rows, column_names, next_nct_id


if __name__ == "__main__":
    df_6648 = pd.read_csv(
        "/Users/mac/thinhquyen/uit/code/cognee_trial/data/trials_6648.csv"
    )
    list_nct_ids = df_6648["nct_id"].unique()

    time_start = time.time()

    rows, column_names, next_nct_id = get_nct_with_eligibility_criteria(list_nct_ids)

    df_eligibility_criteria = pd.DataFrame(rows, columns=column_names)

    df = pd.merge(df_6648, df_eligibility_criteria, on="nct_id", how="left")
    print(df)
    df.to_csv(
        "/Users/mac/thinhquyen/uit/code/LightRAG4Trial/lightrag/custom/data/df_6648_with_eligibility_criteria.csv"
    )
