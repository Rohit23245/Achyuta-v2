import os
import json
import urllib.request
import urllib.error

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_api_config.json")

def get_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "access_token": "EAAUr5Upu4PwBSZBbdMUwcJn9iqnWDws0M5c4vZCKAANhZA4ZAuJ4CNQ8YeUB6aJGk4eeNqon7p86AcAnpmAjKoklFbwFuzNOEvyGZBlHKm3SG6OAppfdPxYrCXH6YAFI052COA6rYEAnvMu2lWFxRhaDbAXgEf0KEkID0b9ZAn44xhSJNkyhUja3KiWuIp7gZDZD",
        "phone_number_id": "1436823629516896",
        "waba_id": "30085683801037446",
        "app_id": "1455638679838972",
        "app_name": "Kavya API Tool",
        "system_user_name": "KavyaBackendSystemUser",
        "default_recipient": "918707526283",
        "api_version": "v22.0"
    }

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def send_template(recipient="918707526283", template_name="hello_world", lang_code="en_US"):
    cfg = get_config()
    clean_to = str(recipient).replace("+", "").replace("-", "").replace(" ", "").strip()
    if not clean_to.startswith("91") and len(clean_to) == 10:
        clean_to = "91" + clean_to

    url = f"https://graph.facebook.com/{cfg.get('api_version', 'v22.0')}/{cfg['phone_number_id']}/messages"
    headers = {
        "Authorization": f"Bearer {cfg['access_token']}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": lang_code
            }
        }
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return {"success": True, "data": data}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode()
        return {"success": False, "status_code": e.code, "error": err_msg}
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_text(recipient="918707526283", text_body="Hello from Achyuta CRM!"):
    cfg = get_config()
    clean_to = str(recipient).replace("+", "").replace("-", "").replace(" ", "").strip()
    if not clean_to.startswith("91") and len(clean_to) == 10:
        clean_to = "91" + clean_to

    url = f"https://graph.facebook.com/{cfg.get('api_version', 'v22.0')}/{cfg['phone_number_id']}/messages"
    headers = {
        "Authorization": f"Bearer {cfg['access_token']}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": clean_to,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text_body
        }
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return {"success": True, "data": data}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode()
        return {"success": False, "status_code": e.code, "error": err_msg}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("Testing WhatsApp Cloud API Dispatch...")
    res = send_template("918707526283", "hello_world")
    print("Result:", json.dumps(res, indent=2))
