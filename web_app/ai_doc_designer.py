import os
import re
import json
import random
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_DOCS_DIR = os.path.join(DATA_DIR, "generated_docs")

# Approved Simple & Sober Corporate Design Standard (Light-only, Clean Paper Letterhead)
PROPOSAL_DESIGN_THEMES = [
    {
        "name": "Sober Corporate Letterhead",
        "palette": "Pure white (#ffffff) sheet on subtle neutral (#f5f5f5) backdrop, 3px solid charcoal (#18181b) top border, muted zinc (#71717a) labels, crisp 1px (#e4e4e7) hairlines, NO dark mode",
        "typography": "Inter (400, 500, 600, 700) everywhere with font-variant-numeric: tabular-nums (NO monospace)",
        "layout": "Clean 2-line letterhead header (Company + contact left, PROPOSAL #ID + Status right), crisp title + 2-line executive summary, 4-column hairline metadata row (human-readable dates), clean deliverables table, Commercial Terms left + right-aligned Subtotal/GST/Total, and bottom Footer Action Bar (Download PDF + Accept Proposal)"
    }
]

INVOICE_DESIGN_THEMES = [
    {
        "name": "Sober Corporate Invoice",
        "palette": "Pure white (#ffffff) sheet on subtle neutral (#f5f5f5) backdrop, 3px solid charcoal (#18181b) top border, muted zinc (#71717a) labels, crisp 1px (#e4e4e7) hairlines, NO dark mode",
        "typography": "Inter (400, 500, 600, 700) everywhere with font-variant-numeric: tabular-nums (NO monospace)",
        "layout": "Clean 2-line letterhead header (Company + contact left, INVOICE #ID + Status right), 4-column hairline metadata row, clean itemized billing table, Commercial Terms left + right-aligned Subtotal/GST/Total, and bottom Footer Action Bar (Download PDF + Pay via UPI)"
    }
]


def _ensure_docs_dir():
    os.makedirs(GENERATED_DOCS_DIR, exist_ok=True)


def get_generated_doc_path(doc_id):
    safe_id = re.sub(r'[^a-zA-Z0-9_\-]', '', str(doc_id or ''))
    if not safe_id:
        return None
    return os.path.join(GENERATED_DOCS_DIR, f"{safe_id}.html")


def load_saved_custom_html(doc_record):
    """
    Returns saved LLM-generated HTML from either the record's `custom_html`
    or `generated_docs/<id>.html` on disk.
    """
    if not isinstance(doc_record, dict):
        return None
    inline_html = doc_record.get("custom_html")
    if isinstance(inline_html, str) and "<html" in inline_html.lower() and "</html>" in inline_html.lower():
        return inline_html

    doc_id = doc_record.get("id")
    path = get_generated_doc_path(doc_id)
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if "<html" in content.lower() and "</html>" in content.lower():
                return content
        except Exception:
            pass
    return None


def save_custom_html_to_disk(doc_id, html_code):
    _ensure_docs_dir()
    path = get_generated_doc_path(doc_id)
    if not path or not html_code:
        return False
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_code)
        return True
    except Exception as e:
        print(f"[AI Doc Designer] Failed saving HTML to {path}: {e}", flush=True)
        return False


def _strip_markdown_fences(raw_text):
    text = (raw_text or "").strip()
    # Remove leading/trailing ```html ... ``` fences
    fence_match = re.search(r'```(?:html|HTML)?\s*\n?(<!DOCTYPE html[\s\S]*?</html>|<html[\s\S]*?</html>)\s*```', text, re.IGNORECASE)
    if fence_match:
        return fence_match.group(1).strip()
    if text.startswith("```"):
        text = re.sub(r'^```[a-zA-Z]*\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
    # Extract from <!DOCTYPE or <html to </html>
    doc_match = re.search(r'(<!DOCTYPE html[\s\S]*?</html>|<html[\s\S]*?</html>)', text, re.IGNORECASE)
    if doc_match:
        return doc_match.group(1).strip()
    return text.strip()


def _is_valid_generated_html(html_code):
    if not html_code or len(html_code) < 600:
        return False
    low = html_code.lower()
    if "<html" not in low or "</html>" not in low:
        return False
    if "<body" not in low or "</body>" not in low:
        return False
    if "<style" not in low:
        return False
    return True


def _resolve_api_key(explicit_key=None):
    if explicit_key and explicit_key.strip() and explicit_key != "YOUR_CHAT_API_KEY":
        return explicit_key.strip()
    env_k = os.environ.get("AI_API_KEY", "").strip()
    if env_k and env_k != "YOUR_CHAT_API_KEY":
        return env_k
    for candidate in [
        os.path.join(os.path.dirname(DATA_DIR), "gemini_api_key.json"),
        os.path.join(DATA_DIR, "gemini_api_key.json"),
    ]:
        if os.path.exists(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    k = d.get("gemini_api_key") or d.get("voice_api_key") or ""
                    if k:
                        return k.strip()
            except Exception:
                pass
    return ""


def _build_document_context(doc_record, comp_settings=None):
    comp = comp_settings if isinstance(comp_settings, dict) else {}
    company_name = comp.get("company_name") or "ACHYUTA ENTERPRISE"
    company_contact = comp.get("contact") or "+91 87075 26283 / contact@achyuta.ai"
    company_gstin = comp.get("gstin") or "07AAAAA0000A1Z5"
    proposal_signatory = comp.get("proposal_signatory") or "Executive Director & Principal Architect"
    upi_id = comp.get("upi_id") or "billing@achyuta"
    wa_phone = re.sub(r'\D', '', str(comp.get("whatsapp") or comp.get("phone") or "918707526283"))
    if len(wa_phone) == 10:
        wa_phone = "91" + wa_phone
    if not wa_phone:
        wa_phone = "918707526283"

    doc_id = str(doc_record.get("id") or "DOC-1001")
    raw_type = str(doc_record.get("type") or "Invoice").strip()
    is_proposal = raw_type.lower() in ("quotation", "proposal", "quote") or doc_id.upper().startswith(("PROP-", "QUO-"))

    client_name = str(doc_record.get("client_name") or "Distinguished Partner").strip()
    client_email = str(doc_record.get("client_email") or "").strip()
    client_phone = str(doc_record.get("client_phone") or "").strip()
    desc = str(doc_record.get("description") or "").strip()
    if not desc:
        items = doc_record.get("items") or []
        if isinstance(items, list) and items and isinstance(items[0], dict):
            desc = str(items[0].get("desc") or "").strip()
    if not desc:
        desc = "Enterprise Digital Transformation & Strategic Implementation" if is_proposal else "Professional Business Consulting & Technology Services"

    subtotal = float(doc_record.get("subtotal") or doc_record.get("amount") or 0.0)
    gst_rate = float(doc_record.get("gst_rate") if doc_record.get("gst_rate") is not None else 18)
    gst_amount = float(doc_record.get("gst_amount") if doc_record.get("gst_amount") is not None else round((subtotal * gst_rate) / 100.0, 2))
    total_amount = float(doc_record.get("total_amount") or doc_record.get("total") or round(subtotal + gst_amount, 2))

    date_val = str(doc_record.get("date") or doc_record.get("invoice_date") or datetime.now().strftime("%Y-%m-%d"))
    due_date = str(doc_record.get("due_date") or (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"))
    status = str(doc_record.get("status") or "Pending").strip()
    notes = str(doc_record.get("notes") or "").strip()

    items = doc_record.get("items")
    if not isinstance(items, list) or not items:
        items = [{
            "desc": desc,
            "hsn": "998314",
            "qty": 1,
            "rate": subtotal,
            "amount": subtotal
        }]

    safe_accept_msg = urllib.parse.quote(
        f"Hello {company_name}, I have reviewed Proposal #{doc_id} for INR {total_amount:,.2f} and approve the deliverables."
    )
    accept_wa_url = f"https://wa.me/{wa_phone}?text={safe_accept_msg}"
    upi_url = f"upi://pay?pa={urllib.parse.quote(upi_id)}&pn={urllib.parse.quote(company_name)}&am={total_amount:.2f}&cu=INR"

    return {
        "is_proposal": is_proposal,
        "doc_type_label": "Executive Proposal & Commercial Quotation" if is_proposal else "Official Tax Invoice",
        "doc_id": doc_id,
        "company_name": company_name,
        "company_contact": company_contact,
        "company_gstin": company_gstin,
        "proposal_signatory": proposal_signatory,
        "client_name": client_name,
        "client_email": client_email,
        "client_phone": client_phone,
        "description": desc,
        "subtotal": subtotal,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,
        "total_amount": total_amount,
        "date": date_val,
        "due_date": due_date,
        "status": status,
        "is_paid": status.lower() in ("paid", "accepted", "approved"),
        "notes": notes,
        "items": items,
        "accept_wa_url": accept_wa_url,
        "upi_url": upi_url,
    }


def generate_custom_document_html(doc_record, comp_settings=None, design_style=None, custom_instructions=None, api_key=None):
    """
    Uses Gemini LLM to dynamically design and write a complete, creative, attractive,
    and print-ready standalone HTML5 document for a Proposal or Invoice.

    Returns (html_code, theme_name) on success, or (None, None) on failure.
    """
    key = _resolve_api_key(api_key)
    if not key:
        print("[AI Doc Designer] No Gemini API key available; using classic fallback.", flush=True)
        return None, None

    ctx = _build_document_context(doc_record, comp_settings)
    pool = PROPOSAL_DESIGN_THEMES if ctx["is_proposal"] else INVOICE_DESIGN_THEMES

    # Pick a theme avoiding the previous theme if regenerating
    prev_theme = doc_record.get("design_theme")
    candidates = [t for t in pool if t["name"] != prev_theme] or pool
    chosen_theme = random.choice(candidates)
    theme_label = design_style.strip() if (design_style and str(design_style).strip()) else chosen_theme["name"]

    if design_style and str(design_style).strip():
        style_spec = f"USER REQUESTED DESIGN STYLE: {design_style.strip()}\n(Craft a bespoke luxury color palette, typography pairing, and layout matching this exact direction.)"
    else:
        style_spec = (
            f"DESIGN THEME: {chosen_theme['name']}\n"
            f"- Color Palette: {chosen_theme['palette']}\n"
            f"- Typography: {chosen_theme['typography']}\n"
            f"- Layout Signature: {chosen_theme['layout']}"
        )

    extra_notes = f"\nADDITIONAL CREATIVE INSTRUCTIONS:\n{custom_instructions.strip()}" if (custom_instructions and str(custom_instructions).strip()) else ""

    if ctx["is_proposal"]:
        doc_requirements = f"""
DOCUMENT TYPE: SOBER CORPORATE COMMERCIAL PROPOSAL
Build an ultra-clean, simple, sober white-paper corporate proposal (NO dark theme, NO theme toggle button, NO flashy gradients, NO signature block).
REQUIRED STRUCTURE:
1. Header: 2-line letterhead with `border-top: 3px solid #18181b` on `.page`. Left: "{ctx['company_name']}" + "{ctx['company_contact']} • GSTIN: {ctx['company_gstin']}". Right: "PROPOSAL #{ctx['doc_id']}" + "Status: {ctx['status']}".
2. Title & Executive Summary: Crisp heading for "{ctx['description']}" + 2-line executive summary tailored to "{ctx['client_name']}"'s business (do NOT repeat "Prepared for..." in the summary).
3. 4-Column Hairline Metadata Row (`border-top` & `border-bottom: 1px solid #e4e4e7`): Prepared For ({ctx['client_name']}), Date ({ctx['date']}), Valid Until ({ctx['due_date']}), Timeline.
4. Clean Deliverables Table: Break down "{ctx['description']}" into 3 realistic phases whose amounts sum cleanly to ₹{ctx['subtotal']:,.2f} with columns: Deliverable, Timeline, Amount.
5. Commercial Terms & Totals (NO bottom border under this section): Left: quiet "Commercial Terms" note. Right: Subtotal (₹{ctx['subtotal']:,.2f}), GST ({ctx['gst_rate']:.0f}%: ₹{ctx['gst_amount']:,.2f}), Total (₹{ctx['total_amount']:,.2f}).
6. Bottom Footer Action Bar (`border-top: 1px solid #e4e4e7`): Left: "Valid until {ctx['due_date']} • Questions? {ctx['company_contact']}". Right: "Download PDF" (`window.print()`) + "Accept Proposal" (`{ctx['accept_wa_url']}`).
"""
    else:
        pay_cta = (
            f'<span style="font-size:13px;font-weight:600;color:#15803d;">Payment Completed</span>'
            if ctx["is_paid"]
            else f'<a href="{ctx["upi_url"]}" class="btn-solid">Pay ₹{ctx["total_amount"]:,.2f} via UPI</a>'
        )
        doc_requirements = f"""
DOCUMENT TYPE: SOBER CORPORATE TAX INVOICE
Build an ultra-clean, simple, sober white-paper corporate tax invoice (NO dark theme, NO theme toggle button, NO flashy gradients, NO signature block).
REQUIRED STRUCTURE:
1. Header: 2-line letterhead with `border-top: 3px solid #18181b` on `.page`. Left: "{ctx['company_name']}" + "{ctx['company_contact']} • GSTIN: {ctx['company_gstin']}". Right: "INVOICE #{ctx['doc_id']}" + "Status: {'Paid' if ctx['is_paid'] else 'Pending Payment'}".
2. 4-Column Hairline Metadata Row: Billed To ({ctx['client_name']}), Invoice Date ({ctx['date']}), Due Date ({ctx['due_date']}), Payment Mode (UPI / Bank).
3. Clean Itemized Table using exact items JSON: {json.dumps(ctx['items'], ensure_ascii=False)} (Description, Qty, Rate, Amount).
4. Commercial Terms & Totals (NO bottom border under this section): Left: quiet "Payment Terms" note. Right: Subtotal (₹{ctx['subtotal']:,.2f}), GST ({ctx['gst_rate']:.0f}%: ₹{ctx['gst_amount']:,.2f}), Total Due (₹{ctx['total_amount']:,.2f}).
5. Bottom Footer Action Bar (`border-top: 1px solid #e4e4e7`): Left: "Due by {ctx['due_date']} • Questions? {ctx['company_contact']}". Right: "Download PDF" (`window.print()`) + {pay_cta}.
"""

    prompt = f"""You are an award-winning Senior Product Designer & Frontend Creative Technologist.
Generate a COMPLETE, standalone, self-contained HTML5 document (`<!DOCTYPE html> ... </html>`) for the following business document.

{style_spec}
{extra_notes}

{doc_requirements}

STRICT ENGINEERING RULES:
1. Output ONLY raw valid HTML5 code starting with `<!DOCTYPE html>` and ending with `</html>`. Do NOT wrap in markdown explanations or commentary.
2. Put ALL CSS inside `<style>` in `<head>` (you may import Google Fonts via `<link>` for typography, plus clean system fallbacks). Do NOT rely on external CSS frameworks like Tailwind CDN so the page renders reliably offline and in PDF print.
3. Make the layout 100% responsive (desktop, tablet, mobile) with refined spacing, subtle micro-shadows, crisp borders, and `@media print` rules (`@page {{ margin: 12mm; }}`, `.no-print {{ display: none !important; }}`, clean light print colors).
4. Keep the total HTML size compact and clean (roughly 8KB to 25KB) with zero emojis unless strictly subtle SVG icons (prefer crisp inline SVGs over emojis!).
5. Every financial number, client name, company name, document ID, UPI link, and WhatsApp link MUST match the exact data provided above.
"""

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.85,
            "maxOutputTokens": 8192
        }
    }

    models_pool = ["gemini-flash-lite-latest", "gemini-3.5-flash", "gemini-2.5-flash"]
    data_bytes = json.dumps(payload).encode("utf-8")

    for model_name in models_pool:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=35) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
            candidates = res_json.get("candidates") or []
            if not candidates:
                continue
            parts = candidates[0].get("content", {}).get("parts", [])
            raw_text = "".join(p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p and not p.get("thought"))
            cleaned_html = _strip_markdown_fences(raw_text)
            if _is_valid_generated_html(cleaned_html):
                save_custom_html_to_disk(ctx["doc_id"], cleaned_html)
                print(f"[AI Doc Designer] Generated bespoke '{theme_label}' HTML ({len(cleaned_html)} bytes) for {ctx['doc_id']} via {model_name}", flush=True)
                return cleaned_html, theme_label
            else:
                print(f"[AI Doc Designer] Output from {model_name} failed HTML validation (len={len(cleaned_html)}), trying next...", flush=True)
        except urllib.error.HTTPError as e:
            err_msg = ""
            try:
                err_msg = e.read().decode("utf-8")[:200]
            except Exception:
                pass
            print(f"[AI Doc Designer] Model {model_name} HTTP {e.code}: {err_msg}", flush=True)
        except Exception as ex:
            print(f"[AI Doc Designer] Model {model_name} error: {ex}", flush=True)

    return None, None
