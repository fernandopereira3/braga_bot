import requests
import re
import time
from dotenv import load_dotenv
import os

load_dotenv()

LOGIN_URL = "https://ead.cecp.sp.gov.br/login/index.php"
USERNAME = os.environ.get("SITE_USERNAME", "")
PASSWORD = os.environ.get("SITE_PASSWORD", "")

MOD_RE = re.compile(
    r'(?:https://ead\.cecp\.sp\.gov\.br)?/mod/([^/"]+)/view\.php\?id=(\d+)'
)
YOUTUBE_RE = re.compile(
    r'https?://(?:www\.)?(?:youtube\.com/watch\?[^\s"\'<>]+|youtu\.be/[^\s"\'<>]+)'
)

session = requests.Session()

r = session.get(LOGIN_URL, timeout=10)
token_match = re.search(r'name="logintoken" value="([^"]+)"', r.text)
logintoken = token_match.group(1) if token_match else ""

r = session.post(
    LOGIN_URL,
    data={
        "username": USERNAME,
        "password": PASSWORD,
        "logintoken": logintoken,
    },
    timeout=10,
    allow_redirects=True,
)

if "login" in r.url:
    print("❌ Login falhou")
    exit(1)

print("✅ Login OK — escaneando...")

for mid in range(1000, 2001):
    book_url = f"https://ead.cecp.sp.gov.br/mod/book/view.php?id={mid}"
    try:
        r = session.get(book_url, timeout=5, allow_redirects=True)
        if "login" in r.url or r.status_code != 200:
            continue

        print(f"  📖 book {mid}\n")

        mod_urls = list(set(MOD_RE.findall(r.text)))
        for mod_type, mod_id in mod_urls:
            mod_url = f"https://ead.cecp.sp.gov.br/mod/{mod_type}/view.php?id={mod_id}"
            print(f"    🔗 {mod_type} encontrado: {mod_url}")
            try:
                rq = session.get(mod_url, timeout=5, allow_redirects=True)
                if "login" in rq.url or rq.status_code != 200:
                    continue
                print("    ✅ acessível\n")

                if mod_type == "simplecertificate":
                    pdf_match = re.search(
                        r'href="([^"]*simplecertificate[^"]*certificate\.php[^"]*)"',
                        rq.text,
                    )
                    if pdf_match:
                        pdf_url = pdf_match.group(1)
                        pdf = session.get(pdf_url, timeout=15)
                        if pdf.headers.get("content-type", "").startswith(
                            "application/pdf"
                        ):
                            filename = f"certificado_{mod_id}.pdf"
                            with open(filename, "wb") as f:
                                f.write(pdf.content)
                            print(f"    💾 salvo: {filename}")
                        else:
                            print(
                                f"    ⚠️  resposta não é PDF: {pdf.headers.get('content-type')}"
                            )
                    else:
                        print("    ⚠️  link do PDF não encontrado na página")

            except requests.RequestException:
                pass

        yt_urls = list(set(YOUTUBE_RE.findall(r.text)))
        for yt_url in yt_urls:
            print(f"    ▶️  youtube: {yt_url}")

    except requests.RequestException:
        pass
    time.sleep(0.5)
