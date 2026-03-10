import pandas as pd


class SpreadsheetSemanticReader:

    def read_excel(self, path: str):

        workbook = pd.ExcelFile(path)

        tables = []

        for sheet in workbook.sheet_names:

            df = workbook.parse(sheet)

            tables.append({
                "sheet": sheet,
                "rows": len(df),
                "columns": list(df.columns),
                "data": df.to_dict(orient="records")
            })

        return tables

    def detect_indicators(self, tables):

        indicators = []

        for table in tables:

            for column in table["columns"]:

                col = column.lower()

                if "preco" in col or "price" in col:
                    indicators.append({
                        "indicator": "price",
                        "sheet": table["sheet"],
                        "column": column
                    })

                if "area" in col:
                    indicators.append({
                        "indicator": "area",
                        "sheet": table["sheet"],
                        "column": column
                    })

                if "lote" in col:
                    indicators.append({
                        "indicator": "lots",
                        "sheet": table["sheet"],
                        "column": column
                    })

        return indicators
