from typing import Any, Dict, List
import pandas as pd


class SpreadsheetSemanticReader:

    def read_excel(self, path: str) -> List[Dict[str, Any]]:

        workbook = pd.ExcelFile(path)

        tables: List[Dict[str, Any]] = []

        for sheet in workbook.sheet_names:

            df = workbook.parse(sheet)

            tables.append({
                "sheet": sheet,
                "rows": len(df),
                "columns": [str(c) for c in df.columns],
                "data": df.fillna("").to_dict(orient="records")
            })

        return tables

    def detect_indicators(self, tables: List[Dict[str, Any]]) -> List[Dict[str, str]]:

        indicators: List[Dict[str, str]] = []

        for table in tables:

            sheet = table["sheet"]

            for column in table["columns"]:

                col = str(column).lower()

                if "preco" in col or "preço" in col or "price" in col:
                    indicators.append({
                        "indicator": "price",
                        "sheet": sheet,
                        "column": column
                    })

                if "area" in col or "área" in col:
                    indicators.append({
                        "indicator": "area",
                        "sheet": sheet,
                        "column": column
                    })

                if "lote" in col:
                    indicators.append({
                        "indicator": "lots",
                        "sheet": sheet,
                        "column": column
                    })

        return indicators
