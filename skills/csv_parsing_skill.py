# skills/csv_parsing_skill.py
from typing import Dict, Any, List, Optional
from core.skill_manager import BaseSkill
from core.logger import log
import csv
import io

class CSVParsingSkill(BaseSkill):
    name: str = "csv_parser"

    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        operation = kwargs.get("operation", "get_csv_headers").lower()
        # CSV data can be passed in prompt or a dedicated 'csv_data' kwarg
        csv_data_str = kwargs.get("csv_data", prompt)

        log.info(f"CSVParsingSkill executing. Operation: '{operation}', CSV data (first 100 chars): '{csv_data_str[:100]}...'")

        if not csv_data_str or not csv_data_str.strip():
            return self._build_response(success=False, error="Input Error", details="CSV data cannot be empty.")

        try:
            # Use io.StringIO to treat the string as a file
            csvfile = io.StringIO(csv_data_str)
            reader = csv.reader(csvfile)
            rows = list(reader) # Read all rows into a list

            if not rows:
                return self._build_response(success=False, error="CSV Error", details="CSV data is empty or invalid.")

            headers = rows[0]
            data_rows = rows[1:]

            if operation == "get_csv_headers":
                return self._build_response(success=True, data={"headers": headers, "num_data_rows": len(data_rows)})

            elif operation == "get_csv_row_by_index":
                row_index = kwargs.get("row_index")
                if row_index is None:
                    return self._build_response(success=False, error="Input Error", details="'row_index' (0-based for data rows) is required.")
                try:
                    row_index = int(row_index)
                    if not (0 <= row_index < len(data_rows)):
                        return self._build_response(success=False, error="Index Error", details=f"Row index {row_index} is out of bounds for {len(data_rows)} data rows.")
                    selected_row = dict(zip(headers, data_rows[row_index]))
                    return self._build_response(success=True, data={"row_index": row_index, "row_data": selected_row})
                except ValueError:
                    return self._build_response(success=False, error="Input Error", details="'row_index' must be an integer.")

            elif operation == "get_csv_column_by_name":
                column_name = kwargs.get("column_name")
                if not column_name:
                    return self._build_response(success=False, error="Input Error", details="'column_name' is required.")
                if column_name not in headers:
                    return self._build_response(success=False, error="Input Error", details=f"Column '{column_name}' not found in headers: {headers}")
                
                col_index = headers.index(column_name)
                column_data = [row[col_index] for row in data_rows]
                return self._build_response(success=True, data={"column_name": column_name, "column_data": column_data[:50], "total_items_in_column": len(column_data)}) # Preview first 50
            
            elif operation == "get_all_data_as_json":
                json_data = [dict(zip(headers, row)) for row in data_rows]
                return self._build_response(success=True, data={"json_data": json_data[:20], "total_rows_converted": len(json_data)}) # Preview first 20

            else:
                return self._build_response(success=False, error="Unsupported Operation", details=f"Operation '{operation}' is not supported.")

        except csv.Error as e:
            log.error(f"CSVParsingSkill CSV processing error: {e}", exc_info=True)
            return self._build_response(success=False, error="CSV Parsing Error", details=str(e))
        except Exception as e:
            log.error(f"CSVParsingSkill unexpected error: {e}", exc_info=True)
            return self._build_response(success=False, error="Internal Skill Error", details=str(e))

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "skill_name": self.name,
            "description": "Parses CSV data provided as a string and allows extraction of headers, rows, or columns.",
            "operations": {
                "get_csv_headers": {
                    "description": "Extracts the header row from the CSV data.",
                    "parameters_schema": {"csv_data": {"type": "string", "description": "The CSV data as a string. Can also be passed via 'prompt'."}},
                    "example_request_payload": {"task_type": self.name, "operation": "get_csv_headers", "csv_data": "header1,header2\nvalue1,value2"}
                },
                "get_csv_row_by_index": {
                    "description": "Extracts a specific data row by its 0-based index.",
                    "parameters_schema": {"csv_data": {"type": "string"}, "row_index": {"type": "integer", "description": "0-based index of the data row to retrieve (excludes header)."}},
                    "example_request_payload": {"task_type": self.name, "operation": "get_csv_row_by_index", "csv_data": "h1,h2\nv1,v2\nv3,v4", "row_index": 0}
                },
                "get_csv_column_by_name": {
                    "description": "Extracts all data from a specific column by its header name.",
                    "parameters_schema": {"csv_data": {"type": "string"}, "column_name": {"type": "string", "description": "The name of the header for the column to retrieve."}},
                    "example_request_payload": {"task_type": self.name, "operation": "get_csv_column_by_name", "csv_data": "name,age\nAlice,30\nBob,24", "column_name": "age"}
                },
                "get_all_data_as_json": {
                    "description": "Converts all data rows (excluding header) into a list of JSON objects (dictionaries).",
                    "parameters_schema": {"csv_data": {"type": "string", "description": "The CSV data as a string."}},
                    "example_request_payload": {"task_type": self.name, "operation": "get_all_data_as_json", "csv_data": "name,age\nAlice,30\nBob,24"}
                }
            }
        }