import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


class Login:
    def __init__(self):
        self.url = "http://ead.cecp.sp.gov.br/login/index.php"
        self.driver = None

    def setup_driver(self):
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
            print("Driver configurado com sucesso")
        except Exception as e:
            print(f"Erro ao configurar driver: {e}")
            raise

    def ping(self):
        while True:
            self.now = time.strftime("%H:%M:%S")
            try:
                ping = requests.get(self.url)
                if ping.status_code == 200:
                    return print(f"Site ON as {self.now}")
            except:
                print(f"Site OFF as {self.now}")
            time.sleep(10)

    def navigate(self):
        if not self.driver:
            raise Exception(
                "Driver não foi inicializado. Chame setup_driver() primeiro."
            )

        try:
            self.driver.get(self.url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("Navegação realizada com sucesso")
        except Exception as e:
            print(f"Erro na navegação: {e}")
            raise

    def find_login_elements(self):
        username = self.driver.find_element(By.XPATH, "//*[@id='username']")
        password = self.driver.find_element(By.XPATH, '//*[@id="password"]')
        login_btn = self.driver.find_element(By.XPATH, '//*[@id="loginbtn"]')

        return username, password, login_btn

    def login(self, user, pwd):
        username, password, login_btn = self.find_login_elements()

        username.send_keys(user)
        password.send_keys(pwd)
        login_btn.click()
        time.sleep(5)

    def get_cursos(self):
        self.driver.find_element(
            By.XPATH, "/html/body/div[3]/nav/div[1]/nav/ul/li[3]/a"
        ).click()
        time.sleep(5)
        self.driver.find_element(
            By.XPATH,
            "/html/body/div[3]/div[3]/div[1]/div[2]/div/section/div/section/section/div/div/div[1]/div[2]/div/div/div[1]/div/div/div[1]/div/a",
        ).click()
        # self.driver.find_element(By.XPATH, "/html/body/div[3]/nav/div[1]/nav/ul/li[3]/ul/li[1]/a").click()

    def processar_cursos(self):
        self.driver.find_element(
            By.XPATH,
            "/html/body/div[3]/div[5]/div[1]/div[3]/div/section/div/div[1]/div/ul",
        )

    # def close(self):
    #    if self.driver:
    #        self.driver.quit()


def main():
    login = Login()
    if login.ping() == 200:
        print("Configurando driver...")
        login.setup_driver()
        print("Navegando para o site...")
        login.navigate()
        print("Fazendo login...")
        login.login("370.768.438-54", "@Leon02023091")
        print("Acessando cursos...")
        login.get_cursos()
        time.sleep(30)
    else:
        login.ping()


if __name__ == "__main__":
    main()
