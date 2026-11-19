import os
import json
import urllib.request
import urllib.error
import re

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_api_config.json")
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_outreach_log.json")

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
        "api_version": "v22.0"
    }

def clean_phone_number(phone):
    digits = re.sub(r'\D', '', str(phone))
    if len(digits) == 10:
        digits = "91" + digits
    return digits

def log_whatsapp_message(recipient, message_type, content, status, message_id=None, error=None):
    logs = []
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    
    import time
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "recipient": recipient,
        "type": message_type,
        "content": content,
        "status": status,
        "message_id": message_id,
        "error": error
    }
    logs.insert(0, entry)
    try:
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(logs[:500], f, indent=2)
    except Exception:
        pass

def send_whatsapp_template(recipient, template_name="hello_world", lang_code="en_US"):
    clean_to = clean_phone_number(recipient)
    cfg = get_config()
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
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            msg_id = data.get("messages", [{}])[0].get("id")
            log_whatsapp_message(clean_to, "template", template_name, "accepted", msg_id)
            return {"success": True, "message_id": msg_id, "data": data}
    except urllib.error.HTTPError as e:
        err_text = e.read().decode()
        log_whatsapp_message(clean_to, "template", template_name, f"HTTP_{e.code}", error=err_text)
        return {"success": False, "status_code": e.code, "error": err_text}
    except Exception as e:
        log_whatsapp_message(clean_to, "template", template_name, "error", error=str(e))
        return {"success": False, "error": str(e)}

def send_whatsapp_custom_text(recipient, message_text):
    clean_to = clean_phone_number(recipient)
    cfg = get_config()
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
            "body": message_text
        }
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            msg_id = data.get("messages", [{}])[0].get("id")
            log_whatsapp_message(clean_to, "text", message_text, "accepted", msg_id)
            return {"success": True, "message_id": msg_id, "data": data}
    except urllib.error.HTTPError as e:
        err_text = e.read().decode()
        # If text failed because 24h window closed, fallback or report
        log_whatsapp_message(clean_to, "text", message_text, f"HTTP_{e.code}", error=err_text)
        return {"success": False, "status_code": e.code, "error": err_text}
    except Exception as e:
        log_whatsapp_message(clean_to, "text", message_text, "error", error=str(e))
        return {"success": False, "error": str(e)}

def dispatch_whatsapp(recipient, message_text=None, template_name=None):
    if template_name:
        return send_whatsapp_template(recipient, template_name=template_name)
    elif message_text:
        # Try custom text first
        res = send_whatsapp_custom_text(recipient, message_text)
        if not res.get("success") and "131047" in str(res.get("error")):
            # Customer service window closed: send hello_world template
            return send_whatsapp_template(recipient, template_name="hello_world")
        return res
    else:
        return send_whatsapp_template(recipient, template_name="hello_world")
