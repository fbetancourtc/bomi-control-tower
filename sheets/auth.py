"""Google Sheets authentication — adapted from proceso-tarificacion-diageo."""

import base64
import json
import os

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_credentials():
    """Build credentials from environment variables.

    Priority:
    1. GOOGLE_SA_KEY (base64-encoded JSON) — for cloud deployment
    2. GOOGLE_SERVICE_ACCOUNT_FILE (file path) — for local dev
    """
    sa_key_b64 = os.environ.get("GOOGLE_SA_KEY", "")
    if sa_key_b64:
        sa_info = json.loads(base64.b64decode(sa_key_b64).decode("utf-8"))
        return Credentials.from_service_account_info(sa_info, scopes=SCOPES)

    sa_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "")
    if sa_file:
        return Credentials.from_service_account_file(sa_file, scopes=SCOPES)

    raise ValueError(
        "No credentials configured. Set GOOGLE_SA_KEY or GOOGLE_SERVICE_ACCOUNT_FILE."
    )


def get_sheets_service(credentials=None):
    if credentials is None:
        credentials = get_credentials()
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)
