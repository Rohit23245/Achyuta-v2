with open(r"C:\Users\pc\Desktop\Achyuta_v2.0\web_app\index.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('function openStaffProfile')
print(text[idx:idx+1500])
