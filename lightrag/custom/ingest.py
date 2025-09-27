import asyncio

import numpy as np
import pandas as pd
from loguru import logger

from lightrag.custom.init_rag import initialize_rag


def create_document_from_row(row, column_names):
    """
    Create a document string from a dataframe row where column names are headers
    and cell content is the content.

    Args:
        row: pandas Series representing a row
        column_names: list of column names

    Returns:
        str: Formatted document string
    """
    document_parts = []

    for col_name in column_names:
        value = row[col_name]

        # Handle different types of values
        if isinstance(value, (list, np.ndarray)):
            # Handle array values
            if len(value) == 0 or (len(value) == 1 and pd.isna(value[0])):
                continue
            # Filter out None/NaN values from arrays
            filtered_values = [
                str(v).strip()
                for v in value
                if not pd.isna(v) and v is not None and str(v).strip() != "nan"
            ]
            if not filtered_values:
                continue
            value_str = ", ".join(filtered_values)
        else:
            # Handle scalar values
            if pd.isna(value) or value is None:
                continue
            value_str = str(value).strip()
            if not value_str or value_str == "nan":
                continue

        if col_name == "nct_id":
            header = f"NCT_ID: {row['nct_id']}"
            document_parts.append(f"{header}")
        else:
            content = f"{col_name.replace('_', ' ').title()}\n{value_str}"
            document_parts.append(content)

    return "\n\n".join(document_parts)


def get_csv_data() -> pd.DataFrame:
    """
    Get the csv data from the csv file
    """
    df_train = pd.read_csv("/Users/mac/thinhquyen/uit/vntrialmatch/data/csv/train.csv")
    df_test = pd.read_csv("/Users/mac/thinhquyen/uit/vntrialmatch/data/csv/test.csv")
    df_validation = pd.read_csv(
        "/Users/mac/thinhquyen/uit/vntrialmatch/data/csv/validation.csv"
    )
    df_gt = pd.concat([df_train, df_test, df_validation], ignore_index=True)

    # only use the first 10 topics
    df_gt = df_gt[df_gt["topic_id"].isin([3, 7, 8, 13, 17, 18, 19, 24, 27, 29])]
    df_gt = df_gt[(df_gt["label"] == 1) | (df_gt["label"] == "Entailment")]
    return df_gt  # type: ignore


async def ingest_trials_data(rag):
    """
    Ingest trial data from the database into LightRAG.

    Args:
        rag: LightRAG instance
        batch_size: Number of trials to fetch per batch
        max_trials: Maximum number of trials to process (None for all)
    """

    df_gt = get_csv_data()

    list_nct_ids = df_gt["NCT_id"].unique()

    df = pd.read_csv(
        "/Users/mac/thinhquyen/uit/code/LightRAG4Trial/lightrag/custom/data/df_6648_with_eligibility_criteria.csv"
    )
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    df = df[df["nct_id"].isin(list_nct_ids)]  # type: ignore
    df = df.drop_duplicates(subset=["nct_id"])  # type: ignore
    column_names = df.columns.tolist()

    # df = df.head(2)
    df = df.reset_index(drop=True)

    # Process each row as a document
    for index, row in df.iterrows():
        # Create document from row
        document = create_document_from_row(row, column_names)

        # Use nct_id as document identifier
        doc_id = row["nct_id"]

        # Insert document into RAG
        rag.insert(
            input=document,
            ids=doc_id,
            file_paths=doc_id,
            # split_by_character=SPLITTER,
            # split_by_character_only=True,
        )

        print(f"Ingested {doc_id} - {index}/{len(df)}")


async def main():
    # Initialize RAG instance
    rag = await initialize_rag()
    logger.info("RAG initialized!")

    await ingest_trials_data(rag)

    await rag.finalize_storages()

    logger.info("Ingestion complete!")


if __name__ == "__main__":
    import nest_asyncio

    nest_asyncio.apply()
    asyncio.run(main())
