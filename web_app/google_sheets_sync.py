import os
import json
import time
import threading
import re
from datetime import datetime

# Google Sheets Sync Engine for Achyuta
# Master database: Google Sheet (1QWIb0zW46OA517IZZzD5V9n4kpiTVJqb4eQzGRM0WJE)
# Flow:
# 1. Sheet -> JSON (Pull on startup and periodic)
# 2. CRM / App -> JSON (Instant 0ms read/write)
# 3. JSON -> Sheet (Async instant push on any change)

SHEET_ID = "1QWIb0zW46OA517IZZzD5V9n4kpiTVJqb4eQzGRM0WJE"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

_creds_path = None
for p in [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials.json.json"),
    os.path.join(os.path.dirname(__file__), "credentials.json.json"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials.json"),
    os.path.join(os.path.dirname(__file__), "credentials.json"),
    "/etc/secrets/credentials.json",
]:
    if os.path.exists(p):
        _creds_path = p
        break

_service = None
_lock = threading.Lock()

def get_sheets_service():
    global _service
    if _service:
        return _service
    if not _creds_path or not os.path.exists(_creds_path):
        # Fallback 1: env var if present on Render
        env_cred = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        if env_cred:
            try:
                from google.oauth2 import service_account
                from googleapiclient.discovery import build
                cred_dict = json.loads(env_cred)
                creds = service_account.Credentials.from_service_account_info(cred_dict, scopes=SCOPES)
                _service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
                return _service
            except Exception as e:
                print(f"[Sheets Sync] Error initializing from env: {e}", flush=True)

        # Fallback 2: embedded credentials module
        try:
            from web_app.embedded_sheets_creds import SERVICE_ACCOUNT_INFO
        except ImportError:
            try:
                from embedded_sheets_creds import SERVICE_ACCOUNT_INFO
            except ImportError:
                SERVICE_ACCOUNT_INFO = None

        if SERVICE_ACCOUNT_INFO:
            try:
                from google.oauth2 import service_account
                from googleapiclient.discovery import build
                creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
                _service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
                return _service
            except Exception as e:
                print(f"[Sheets Sync] Error initializing from embedded creds: {e}", flush=True)

        return None

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        creds = service_account.Credentials.from_service_account_file(_creds_path, scopes=SCOPES)
        _service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
        return _service
    except Exception as e:
        print(f"[Sheets Sync] Service init error: {e}", flush=True)
        return None

def normalize_phone(phone_str):
    if not phone_str:
        return ""
    digits = re.sub(r'\D', '', str(phone_str))
    return digits[-10:] if len(digits) >= 10 else digits

def pull_clients_from_sheet_to_vault(clients_vault_path):
    """
    Reads Sheet1!A:C (Company Name, Whatsapp Number, Email)
    Merges fresh leads into clients_vault.json
    """
    svc = get_sheets_service()
    if not svc:
        print("[Sheets Sync] Service not available for pull", flush=True)
        return False, "Google Sheets API service unavailable"

    try:
        res = svc.spreadsheets().values().get(spreadsheetId=SHEET_ID, range="Sheet1!A:C").execute()
        rows = res.get('values', [])
        if not rows:
            return True, "No rows in sheet"

        existing_clients = []
        if os.path.exists(clients_vault_path):
            try:
                with open(clients_vault_path, "r", encoding="utf-8") as f:
                    existing_clients = json.load(f)
            except:
                existing_clients = []

        existing_phones = {normalize_phone(c.get("phone", "")) for c in existing_clients if c.get("phone")}
        new_added = 0

        # Skip header if it contains 'Coumpany' or 'Company'
        start_idx = 1 if rows and any('company' in str(cell).lower() or 'coumpany' in str(cell).lower() for cell in rows[0]) else 0

        for idx, row in enumerate(rows[start_idx:]):
            if not row or not any(row):
                continue
            name = str(row[0]).strip() if len(row) > 0 and row[0] else ""
            phone = str(row[1]).strip() if len(row) > 1 and row[1] else ""
            email = str(row[2]).strip() if len(row) > 2 and row[2] else ""

            if not name and not phone:
                continue

            clean_p = normalize_phone(phone)
            if clean_p and clean_p in existing_phones:
                # Update email/name if missing
                continue

            new_client = {
                "id": f"client_sheet_{start_idx + idx + 1}_{int(time.time())}",
                "name": name or f"Lead {clean_p}",
                "company": name or "Enterprise Lead",
                "phone": clean_p or phone,
                "email": email or "",
                "status": "Lead",
                "source": "Google Sheet",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            existing_clients.append(new_client)
            if clean_p:
                existing_phones.add(clean_p)
            new_added += 1

        if new_added > 0 or not os.path.exists(clients_vault_path):
            with open(clients_vault_path, "w", encoding="utf-8") as f:
                json.dump(existing_clients, f, ensure_ascii=False, indent=2)
            print(f"[Sheets Sync] Pulled and merged {new_added} new leads from Google Sheet! Total: {len(existing_clients)}", flush=True)

        return True, f"Synced {new_added} new leads from Google Sheet"

    except Exception as e:
        print(f"[Sheets Sync] Pull error: {e}", flush=True)
        return False, str(e)

def push_client_to_sheet_async(client_data):
    """
    Non-blocking push of newly created / updated client to Google Sheet.
    Appends to Sheet1: [Company/Name, Phone, Email]
    """
    def _worker():
        svc = get_sheets_service()
        if not svc:
            return
        name = client_data.get("name") or client_data.get("company") or "Client"
        phone = client_data.get("phone") or ""
        email = client_data.get("email") or ""

        body = {
            "values": [[name, phone, email]]
        }
        try:
            svc.spreadsheets().values().append(
                spreadsheetId=SHEET_ID,
                range="Sheet1!A:C",
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            print(f"[Sheets Sync] Successfully pushed client '{name}' ({phone}) to Google Sheet!", flush=True)
        except Exception as e:
            print(f"[Sheets Sync] Push error: {e}", flush=True)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()

def start_periodic_sheets_sync(clients_vault_path, interval_sec=180):
    # Master DB is now CRM_* tabs via pull_all_vaults_from_sheet / sync_vault_to_sheet_async;
    # do not re-import deleted leads from legacy Sheet1.
    return
    """
    Periodically checks Google Sheet for newly added leads and pulls into JSON.
    """
    def _loop():
        # First initial pull
        time.sleep(3)
        pull_clients_from_sheet_to_vault(clients_vault_path)
        while True:
            time.sleep(interval_sec)
            try:
                pull_clients_from_sheet_to_vault(clients_vault_path)
            except Exception as e:
                print(f"[Sheets Sync Loop] Error: {e}", flush=True)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()


CRM_VAULT_TABS = {
    "clients_vault.json": "CRM_Clients",
    "tasks_vault.json": "CRM_Tasks",
    "accounts_vault.json": "CRM_Accounts",
    "invoices_vault.json": "CRM_Invoices",
    "proposals_vault.json": "CRM_Proposals",
    "salary_vault.json": "CRM_Salary",
    "attendance_vault.json": "CRM_Attendance",
    "calling_lists_vault.json": "CRM_CallingLists",
    "call_logs_vault.json": "CRM_CallLogs",
    "campaigns_vault.json": "CRM_Campaigns",
    "contracts_vault.json": "CRM_Contracts",
    "employees_vault.json": "CRM_Employees",
    "meetings_vault.json": "CRM_Meetings",
    "reminders_vault.json": "CRM_Reminders",
    "tickets_vault.json": "CRM_Tickets",
    "users_vault.json": "CRM_Users",
}

def _ensure_sheet_tab(service, tab_name):
    try:
        meta = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
        titles = [s["properties"]["title"] for s in meta.get("sheets", [])]
        if tab_name not in titles:
            service.spreadsheets().batchUpdate(
                spreadsheetId=SHEET_ID,
                body={"requests": [{"addSheet": {"properties": {"title": tab_name}}}]}
            ).execute()
    except Exception as e:
        print(f"[Sheets Sync] Ensure tab {tab_name} error: {e}", flush=True)

def sync_vault_to_sheet_async(vault_filename, vault_path):
    tab_name = CRM_VAULT_TABS.get(vault_filename)
    if not tab_name:
        return
    def _push():
        try:
            service = get_sheets_service()
            if not service or not os.path.exists(vault_path):
                return
            _ensure_sheet_tab(service, tab_name)
            with open(vault_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                return
            rows = [["id", "json_data"]]
            for idx, item in enumerate(data):
                rid = str(item.get("id") or idx) if isinstance(item, dict) else str(idx)
                serialized = json.dumps(item, ensure_ascii=False)
                # Guard against Google Sheets 50,000-character per-cell limit
                if len(serialized) > 48000 and isinstance(item, dict) and "custom_html" in item:
                    compact_item = {k: v for k, v in item.items() if k != "custom_html"}
                    serialized = json.dumps(compact_item, ensure_ascii=False)
                rows.append([rid, serialized])
            service.spreadsheets().values().clear(
                spreadsheetId=SHEET_ID, range=f"{tab_name}!A:B"
            ).execute()
            service.spreadsheets().values().update(
                spreadsheetId=SHEET_ID,
                range=f"{tab_name}!A1",
                valueInputOption="RAW",
                body={"values": rows}
            ).execute()
            print(f"[Sheets Sync] Synced {len(data)} records to {tab_name}!", flush=True)
        except Exception as e:
            print(f"[Sheets Sync] Push {tab_name} error: {e}", flush=True)
    threading.Thread(target=_push, daemon=True).start()

def pull_all_vaults_from_sheet(web_app_dir):
    try:
        service = get_sheets_service()
        if not service:
            return
        for vault_file, tab_name in CRM_VAULT_TABS.items():
            try:
                _ensure_sheet_tab(service, tab_name)
                res = service.spreadsheets().values().get(
                    spreadsheetId=SHEET_ID, range=f"{tab_name}!A:B"
                ).execute()
                vals = res.get("values", [])
                if len(vals) >= 1:
                    items = []
                    for row in vals[1:]:
                        if len(row) >= 2 and row[1]:
                            items.append(json.loads(row[1]))
                    vpath = os.path.join(web_app_dir, vault_file)
                    with open(vpath, "w", encoding="utf-8") as f:
                        json.dump(items, f, ensure_ascii=False, indent=2)
                    print(f"[Sheets Sync] Restored {len(items)} records from {tab_name} -> {vault_file}", flush=True)
            except Exception as te:
                print(f"[Sheets Sync] Pull {tab_name} error: {te}", flush=True)
    except Exception as e:
        print(f"[Sheets Sync] Pull all vaults error: {e}", flush=True)
