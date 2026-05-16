import re
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
)
import time

MOD_RE = re.compile(
    r'(?:https://ead\.cecp\.sp\.gov\.br)?/mod/([^/"]+)/view\.php\?id=(\d+)'
)
SITE_BASE = "https://ead.cecp.sp.gov.br"
NEXT_SELECTOR = "#next-activity-link"


class CourseRunner:
    COMPLETE_BTN_SELECTOR = "button[data-action='toggle-manual-completion']"

    def __init__(self, driver, wait, session, page_delay=5.0, username="", fullname=""):
        self.driver = driver
        self.wait = wait
        self.session = session
        self.page_delay = page_delay
        self.username = username
        self.fullname = fullname
        self.current_course_name = ""

    def _page_ready(self):
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def _click(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", element
        )
        time.sleep(0.2)
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)

    def _get_course_name(self):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
        except NoSuchElementException:
            return ""

    def _get_progress(self):
        try:
            el = self.driver.find_element(
                By.CSS_SELECTOR, "[data-numcomplete][data-numoutof]"
            )
            done = int(el.get_attribute("data-numcomplete"))
            total = int(el.get_attribute("data-numoutof"))
            pct = int(done / total * 100) if total else 0
            return done, total, pct
        except Exception:
            return None, None, None

    def _try_mark_complete_on_page(self):
        btns = self.driver.find_elements(By.CSS_SELECTOR, self.COMPLETE_BTN_SELECTOR)
        for btn in btns:
            if btn.get_attribute("aria-checked") != "true":
                self._click(btn)
                time.sleep(0.5)
                return True
        return False

    def _get_next_url(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            el = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, NEXT_SELECTOR))
            )
            href = el.get_attribute("href")
            print(f"      ➡️  próxima: {href}")
            return href
        except TimeoutException:
            print("      🔚 sem #next-activity-link — fim da cadeia")
            return None

    def _download_certificate(self, mod_id, page_html):
        sesskey_match = re.search(r'name="sesskey"\s+value="([^"]+)"', page_html)
        if not sesskey_match:
            print("    ⚠️  sesskey não encontrado na página do certificado")
            return
        sesskey = sesskey_match.group(1)
        username = self.username or os.environ.get("SITE_USERNAME", "")
        course_name = re.sub(
            r"[^A-Za-z0-9_\-]", "_", self.current_course_name or "Curso"
        )
        safe_user = re.sub(r"[^A-Za-z0-9_\-]", "_", username)
        cert_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "cert", safe_user
        )
        os.makedirs(cert_dir, exist_ok=True)
        try:
            pdf = self.session.post(
                f"{SITE_BASE}/mod/simplecertificate/view.php",
                data={"id": mod_id, "action": "get", "sesskey": sesskey},
                timeout=15,
            )
            if pdf.headers.get("content-type", "").startswith("application/pdf"):
                filename = os.path.join(cert_dir, f"{course_name}.pdf")
                with open(filename, "wb") as f:
                    f.write(pdf.content)
                print(f"    💾 certificado salvo: {filename}")
            else:
                print(f"    ⚠️  resposta não é PDF: {pdf.headers.get('content-type')}")
        except Exception as e:
            print(f"    ⚠️  erro ao baixar certificado: {e}")

    def _submit_feedback(self):
        complete_link = re.search(
            r'href="([^"]*feedback/complete\.php[^"]*)"', self.driver.page_source
        )
        if not complete_link:
            print("    ⚠️  link complete.php não encontrado no feedback")
            return
        complete_url = complete_link.group(1).replace("&amp;", "&")
        self.driver.get(complete_url)
        self._page_ready()
        time.sleep(1)

        self.driver.execute_script("""
            const done = new Set();
            document.querySelectorAll("input[type='radio']").forEach(r => {
                if (!done.has(r.name)) {
                    const group = document.querySelectorAll("input[type='radio'][name='" + r.name + "']");
                    group[group.length - 1].checked = true;
                    group[group.length - 1].dispatchEvent(new Event('change', {bubbles: true}));
                    done.add(r.name);
                }
            });
        """)

        self.driver.execute_script("""
            document.querySelectorAll("input[type='text'], textarea").forEach(f => {
                f.value = 'Muito bom.';
                f.dispatchEvent(new Event('input', {bubbles: true}));
            });
        """)

        self.driver.execute_script(
            "document.querySelector(\"input[name='savevalues']\").click();"
        )
        self._page_ready()
        print("    ✅ feedback enviado")

    def _open_activity(self, url):
        # Quiz: visita só para pegar próxima URL, não interage
        if "/mod/quiz/" in url:
            print(f"    ⚠️  quiz ignorado: {url}")
            self.driver.get(url)
            self._page_ready()
            return self._get_next_url()

        print(f"    🔗 abrindo: {url}")
        self.driver.get(url)
        self._page_ready()
        time.sleep(self.page_delay)
        self._try_mark_complete_on_page()

        if "/mod/feedback/" in url:
            self._submit_feedback()
            return self._get_next_url()

        if "/mod/simplecertificate/" in url:
            mid = re.search(r"\?id=(\d+)", url)
            if mid:
                self._download_certificate(mid.group(1), self.driver.page_source)
            return None

        return self._get_next_url()

    def run_course(self, course_id, course_url):
        self.driver.get(course_url)
        self._page_ready()
        try:
            self.wait.until(lambda d: "/mod/" in d.page_source)
        except Exception:
            pass
        self.current_course_name = self._get_course_name() or f"Curso_{course_id}"

        # Coleta todas as URLs em ordem de aparição (usada como fallback)
        html = self.driver.page_source
        all_urls = []
        seen = set()
        for t, i in MOD_RE.findall(html):
            url = f"{SITE_BASE}/mod/{t}/view.php?id={i}"
            if url not in seen:
                seen.add(url)
                all_urls.append(url)

        if not all_urls:
            print(f"  [{course_id}] nenhuma atividade encontrada")
            return

        print(
            f"  [{course_id}] {len(all_urls)} atividade(s) na página — seguindo next-activity..."
        )

        visited = set()
        current_url = all_urls[0]
        count = 0

        while current_url:
            if current_url in visited:
                # Loop detectado — pula para próxima não visitada da lista
                remaining = [u for u in all_urls if u not in visited]
                if not remaining:
                    break
                current_url = remaining[0]
                print(f"      🔄 loop detectado, retomando lista: {current_url}")
                continue

            visited.add(current_url)
            count += 1
            next_url = self._open_activity(current_url)

            if next_url:
                current_url = next_url
            else:
                # Sem next-activity — fallback para próxima não visitada da lista
                remaining = [u for u in all_urls if u not in visited]
                if remaining:
                    current_url = remaining[0]
                    print(f"      🔄 retomando lista: {current_url}")
                else:
                    break

        print(f"  [{course_id}] {count} atividade(s) navegada(s)")

        self.driver.get(course_url)
        self._page_ready()
        nome = self._get_course_name() or f"Curso {course_id}"
        done, total, pct = self._get_progress()
        print(f"  [{course_id}] {nome} — {done}/{total} ({pct}%)")
