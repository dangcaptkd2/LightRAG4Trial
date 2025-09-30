import asyncio
import json

import numpy as np
import pandas as pd

from lightrag.base import QueryParam
from lightrag.custom.init_rag import initialize_rag
from lightrag.utils import logger


async def query(rag, query: str, query_param: QueryParam):
    result = await rag.aquery(query, query_param)
    logger.info("Query completed!!")
    return result


def get_data():
    data_1 = pd.read_csv("lightrag/custom/data/train.csv")
    data_2 = pd.read_csv("lightrag/custom/data/test.csv")
    data_3 = pd.read_csv("lightrag/custom/data/validation.csv")
    data = pd.concat([data_1, data_2, data_3])
    data = data[data["topic_id"].isin([3, 7, 8, 13, 17, 18, 19, 24, 27, 29])]
    data = data[(data["label"] == 1) | (data["label"] == "Entailment")]
    return pd.DataFrame(data)


def score(pred, gt):
    pred, gt = set(pred), set(gt)
    tp = len(pred & gt)
    fp = len(pred - gt)
    fn = len(gt - pred)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return precision, recall, f1


def score_macro(list_pred, list_gt):
    precisions, recalls, f1s = [], [], []
    for pred, gt in zip(list_pred, list_gt):
        p, r, f = score(pred, gt)
        precisions.append(p)
        recalls.append(r)
        f1s.append(f)
    return np.mean(precisions), np.mean(recalls), np.mean(f1s)


def score_micro(list_pred, list_gt):
    preds = [p for pred in list_pred for p in pred]
    gts = [g for gt in list_gt for g in gt]
    return score(preds, gts)


async def eval():
    # Disable caching for this run
    from lightrag.settings import settings

    settings.llm_settings.enable_llm_cache = False
    settings.llm_settings.enable_llm_cache_for_extract = False

    data = get_data()

    rag = await initialize_rag()

    list_pred, list_gt = [], []
    for topic_id in data["topic_id"].unique():
        gt = data.loc[data["topic_id"] == topic_id, "NCT_id"].unique()
        query_param = QueryParam(
            mode="hybrid",
            only_need_context=False,
            only_need_prompt=False,
            response_type="Single Paragraph",
            stream=False,
            top_k=20,
            chunk_top_k=20,
            max_entity_tokens=10000,
            max_relation_tokens=10000,
            enable_rerank=False,
        )
        patient_profile = data.loc[
            data["topic_id"] == topic_id, "statement_medical"
        ].iloc[0]
        a = await query(rag, str(patient_profile), query_param)
        try:
            a = json.loads(a)
        except Exception:
            print(">> a: ", a)
            a = []
        pred = a
        # pred = list(set([i["file_path"] for i in a]))
        print(f">> Returned chunks: {len(pred)} - Number of GT: {len(gt)}")
        list_pred.append(pred)
        list_gt.append(gt)

    precision, recall, f1 = score_micro(list_pred, list_gt)
    print(f"Micro Precision: {precision}, Micro Recall: {recall}, Micro F1: {f1}")
    precision, recall, f1 = score_macro(list_pred, list_gt)
    print(f"Macro Precision: {precision}, Macro Recall: {recall}, Macro F1: {f1}")


if __name__ == "__main__":
    asyncio.run(eval())
