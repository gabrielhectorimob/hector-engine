import pandas as pd
from rag.indexer import index_document

def index_excel(file):

    sheets = [
        "HECTOR_BRAIN",
        "HECTOR_BENCHMARK",
        "HECTOR_CONTEXT",
        "HECTOR_MODELO"
    ]

    for sheet in sheets:

        df = pd.read_excel(file, sheet_name=sheet)

        for _, row in df.iterrows():

            text = " ".join([str(v) for v in row.values])

            metadata = {
                "sheet": sheet
            }

            index_document(text, metadata)
