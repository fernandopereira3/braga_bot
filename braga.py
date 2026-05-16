import re
import requests
import subprocess
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
# from app_course import CourseRunner

load_dotenv()

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.md")
PAGE_DELAY = float(os.environ.get("PAGE_DELAY", "5"))
ENROL_ID_MAX = int(os.environ.get("ENROL_ID_MAX", "100"))


def load_users():
    if os.path.exists(USERS_FILE):
        users = []
        with open(USERS_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    username, password = line.split(":", 1)
                    users.append((username, password))
        return users
    u = os.environ.get("SITE_USERNAME", "")
    p = os.environ.get("SITE_PASSWORD", "")
    return [(u, p)] if u and p else []


class BragaBot:
    LOGIN_URL = "https://ead.cecp.sp.gov.br/login/index.php"
    COURSE_BASE_URL = "https://ead.cecp.sp.gov.br/course/view.php?id={}"
    TIMEOUT = 15

    def __init__(self):
        self.driver = None
        self.wait = None

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.TIMEOUT)
        print("✅ Driver configurado")

    def wait_for_site(self):
        while True:
            try:
                r = requests.get(self.LOGIN_URL, timeout=5)
                if r.status_code == 200:
                    break
            except requests.RequestException:
                pass
            print("⏳ Site não acessível. Aguardando 10s...")
            time.sleep(10)
        print("✅ Site acessível")

    def login(self, username, password):
        self.driver.delete_all_cookies()
        self.driver.get(self.LOGIN_URL)
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#username")))

        print(f"🔐 Login: {username} | Senha: {'*' * len(password)}")
        self.driver.execute_script(
            "document.querySelector('#username').value = arguments[0];"
            "document.querySelector('#password').value = arguments[1];",
            username,
            password,
        )
        self.driver.find_element(By.CSS_SELECTOR, "#loginbtn").click()
        self.wait.until(EC.url_changes(self.LOGIN_URL))

        if "login" in self.driver.current_url:
            raise RuntimeError(f"Login falhou para {username}")
        print("✅ Login realizado")

    def _get_user_fullname(self):
        try:
            el = self.driver.find_element(
                By.CSS_SELECTOR,
                ".usertext, [data-region='user-menu-content'] .username, .usermenu .usertext",
            )
            return el.text.strip()
        except Exception:
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, "a[title] .usertext")
                return el.text.strip()
            except Exception:
                return ""

    def _get_session(self):
        session = requests.Session()
        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"])
        return session

    def scan_courses(self):
        print("🔍 Buscando cursos matriculados em /my/courses.php...")
        self.driver.get("https://ead.cecp.sp.gov.br/my/courses.php")
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)

        ids = list(
            set(re.findall(r"course/view\.php\?id=(\d+)", self.driver.page_source))
        )
        print(f"  {len(ids)} curso(s) encontrado(s): {ids}")

        incompletos = []
        for course_id in ids:
            url = self.COURSE_BASE_URL.format(course_id)
            self.driver.get(url)
            self.wait.until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(1)
            html = self.driver.page_source

            nome_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
            nome = (
                re.sub(r"<[^>]+>", "", nome_match.group(1)).strip()
                if nome_match
                else f"Curso {course_id}"
            )

            m_done = re.search(r'data-numcomplete="(\d+)"', html)
            m_total = re.search(r'data-numoutof="(\d+)"', html)
            if m_done and m_total:
                done = int(m_done.group(1))
                total = int(m_total.group(1))
                pct = int(done / total * 100) if total else 0
                if total > 0 and done == total:
                    print(
                        f"  ✅ [{course_id}] {nome} — {done}/{total} (100%) — já concluído"
                    )
                    continue
                print(
                    f"  📝 [{course_id}] {nome} — {done}/{total} ({pct}%) — incompleto"
                )
            else:
                print(f"  📝 [{course_id}] {nome} — sem progresso registrado")

            incompletos.append((course_id, url))

        print(f"  {len(incompletos)} curso(s) para completar")
        return incompletos

    def inscrever_em_curso(self, course_ids):
        # id_submitbutton

        for course_id in course_ids:
            print(f"✏️ Inscrevendo no curso {course_id}...")
            self.driver.get(
                f"https://ead.cecp.sp.gov.br/enrol/index.php?id={course_id}"
            )
            self.wait.until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2) 
            try:
                submit_btn = self.driver.find_element(
                    By.CSS_SELECTOR, "#id_submitbutton"
                )
                if submit_btn.get_attribute("value") == "Inscreva-me":
                    submit_btn.click()
                    self.wait.until(
                        lambda d: (
                            d.execute_script("return document.readyState") == "complete"
                        )
                    )
                    print(f"✅ [{course_id}] Inscrição realizada")
            except NoSuchElementException:
                pass
            except Exception as e:
                print(f"❌ [{course_id}] Falha ao inscrever: {e}")

    def run_for_user(self, username, password):
        subprocess.run("cls" if os.name == "nt" else "clear")
        print(f"\n{'=' * 50}")
        print(f"👤 Processando: {username}")
        print(f"{'=' * 50}")
        self.login(username, password)
        # fullname = self._get_user_fullname()
        self.inscrever_em_curso(range(1, ENROL_ID_MAX + 1))
        incompletos = self.scan_courses()
        if not incompletos:
            print("  Nenhum curso para completar.")
            time.sleep(10)
            return
        print(f"\n📋 {len(incompletos)} curso(s) para completar:") # enviar via Twilio no futuro
        for course_id, url in incompletos:
            print(f"  • [{course_id}] {url}")

        # runner = CourseRunner(
        #     self.driver,
        #     self.wait,
        #     self._get_session(),
        #     PAGE_DELAY,
        #     username=username,
        #     fullname=fullname,
        # )
        # for course_id, url in incompletos:
        #     runner.run_course(course_id, url)

    def run(self):
        try:
            subprocess.run("cls" if os.name == "nt" else "clear")
            print("🤖 Iniciando Braga")
            users = load_users()
            if not users:
                print("❌ Nenhum usuário encontrado em users ou variáveis de ambiente.")
                return
            print(f"👥 {len(users)} usuário(s) carregado(s)")
            self.wait_for_site()
            self.setup_driver()
            for username, password in users:
                try:
                    self.run_for_user(username, password)
                except Exception as e:
                    print(f"❌ Erro no usuário {username}: {e}")
            print("\n✅ Todos os usuários processados!")
        except Exception as e:
            print(f"❌ Erro geral: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                print("🧹 Driver fechado")


if __name__ == "__main__":
    BragaBot().run()
