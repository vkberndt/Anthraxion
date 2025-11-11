import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any

# Sheets Headers
SHEET_HEADERS = [
    "Timestamp",
    "Alderon Name",
    "Alderon ID",
    "Rule(s) Broken",
    "Ticket ID",
    "Verdict",
    "Admin",
    "Player Informed?"
]

class SheetsClient:
    def __init__(self, credentials_dict: Dict[str, Any], sheet_name: str, tab_name: str):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        self.gc = gspread.authorize(creds)
        self.sheet_name = sheet_name
        self.tab_name = tab_name

        self.sh = self.gc.open(self.sheet_name)
        try:
            self.ws = self.sh.worksheet(self.tab_name)
        except gspread.WorksheetNotFound:
            self.ws = self.sh.add_worksheet(title=self.tab_name, rows=100, cols=len(SHEET_HEADERS))

        # I ensure headers are correct and in order.
        self._ensure_headers()

    def _ensure_headers(self):
        # Read the first row; if it doesn't match, overwrite it.
        existing = self.ws.row_values(1)
        if existing != SHEET_HEADERS:
            self.ws.resize(rows=max(self.ws.row_count, 100), cols=len(SHEET_HEADERS))
            self.ws.update("A1:H1", [SHEET_HEADERS])

    def append_infraction_row(self, row_values: List[str]):
        # Append directly after the last filled row.
        self.ws.append_row(row_values, value_input_option="USER_ENTERED")

    def query_by_alderon(self, name: str = None, alderon_id: str = None) -> List[List[str]]:
        # Fetch all values once and filter locally to avoid rate limits.
        data = self.ws.get_all_values()
        if not data or len(data) < 2:
            return []

        headers = data[0]
        rows = data[1:]

        # Map headers to indices for stable access even if order changes.
        idx = {h: i for i, h in enumerate(headers)}

        results = []
        for r in rows:
            if name and r[idx.get("Alderon Name", -1)] == name:
                results.append(r)
            elif alderon_id and r[idx.get("Alderon ID", -1)] == alderon_id:
                results.append(r)

        return results