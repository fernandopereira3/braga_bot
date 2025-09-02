import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


class BragaBot:
    # Constantes
    URL = "http://ead.cecp.sp.gov.br/login/index.php"
    USERNAME = ""
    PASSWORD = ""
    TIMEOUT = 10

    # Seletores otimizados
    SELECTORS = {
        "username": "#username",
        "password": "#password",
        "login_btn": "#loginbtn",
        "menu_cursos": "//nav//li[3]/a",
        "primeiro_curso": "//section//div[1]//a",
        "modulos_list": "//section//ul/li",
        "modulos_concluidos": "//ul/li/div[2]/i",
        "modulo_12": "//ul/li[12]",
        "play_button": "//li[12]//a[contains(@class, 'play') or contains(text(), 'Play')]",
    }

    def __init__(self):
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """Configura o driver do Chrome com opções otimizadas"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.TIMEOUT)
        print("✅ Driver configurado")

    def check_connectivity(self):
        """Verifica se o site está acessível"""
        try:
            response = requests.get(self.URL, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def wait_for_site(self):
        """Aguarda o site ficar acessível"""
        while not self.check_connectivity():
            print("⏳ Site não acessível. Aguardando 10s...")
            time.sleep(10)
        print("✅ Site acessível")

    def navigate_and_login(self):
        """Navega para o site e faz login"""
        self.driver.get(self.URL)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Login
        self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.SELECTORS["username"]))
        ).send_keys(self.USERNAME)
        self.driver.find_element(By.CSS_SELECTOR, self.SELECTORS["password"]).send_keys(
            self.PASSWORD
        )
        self.driver.find_element(By.CSS_SELECTOR, self.SELECTORS["login_btn"]).click()

        self.wait.until(EC.url_changes(self.URL))
        print("✅ Login realizado")

    def access_course(self):
        """Acessa o curso e retorna informações dos módulos"""
        # Navegar para cursos
        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, self.SELECTORS["menu_cursos"]))
        ).click()
        time.sleep(2)

        # Selecionar primeiro curso
        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, self.SELECTORS["primeiro_curso"]))
        ).click()
        time.sleep(2)

        # Contar módulos
        modulos = self.wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, self.SELECTORS["modulos_list"])
            )
        )
        total_modulos = len(modulos)

        # Contar módulos concluídos
        try:
            concluidos = self.driver.find_elements(
                By.XPATH, self.SELECTORS["modulos_concluidos"]
            )
            total_concluidos = len(concluidos)
        except:
            total_concluidos = 0

        print(f"📊 Módulos: {total_concluidos}/{total_modulos} concluídos")

        # Acessar módulo 12
        try:
            modulo_12 = self.driver.find_element(By.XPATH, self.SELECTORS["modulo_12"])
            modulo_12.click()
            time.sleep(1)

            # Clicar no play
            play_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, self.SELECTORS["play_button"]))
            )
            play_btn.click()
            print("▶️ Módulo 12 iniciado")

        except Exception as e:
            print(f"⚠️ Erro ao acessar módulo 12: {e}")

        return total_modulos, total_concluidos

    def run(self):
        """Executa o fluxo completo do bot"""
        try:
            print("🤖 Iniciando Braga Bot...")

            # Verificar conectividade
            self.wait_for_site()

            # Configurar driver
            self.setup_driver()

            # Login e navegação
            self.navigate_and_login()

            # Acessar curso
            total, concluidos = self.access_course()

            print(f"✅ Processo concluído! {concluidos}/{total} módulos")

        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Limpa recursos"""
        if self.driver:
            self.driver.quit()
            print("🧹 Driver fechado")


def main():
    bot = BragaBot()
    bot.run()


if __name__ == "__main__":
    main()
