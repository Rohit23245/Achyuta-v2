with open(r"C:\Users\pc\Desktop\Achyuta_v2.0\web_app\index.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('id="staff-profile-modal"')
print(text[idx+4000:idx+6000])
