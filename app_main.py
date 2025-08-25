import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class Login:

    def __init__(self):
        self.url = "https://ead.cecp.sp.gov.br/login/index.php"
        self.driver = None
        
    def setup_driver(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def ping(self):
        while True:
            self.now = time.strftime("%H:%M:%S")
            try:
                ping = requests.get(self.url)
                if ping.status_code == 200:
                    return print(f'Site ON as {self.now}')
            except:
                print(f'Site OFF as {self.now}')
            time.sleep(5)
        
    def navigate(self):
        self.driver.get(self.url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
    def find_login_elements(self):
        username = self.driver.find_element(By.XPATH, "//*[@id='username']")
        password = self.driver.find_element(By.XPATH, "//*[@id=\"password\"]")
        login_btn = self.driver.find_element(By.XPATH, "//*[@id=\"loginbtn\"]")
        
        return username, password, login_btn
        
    def login(self, user, pwd):
        username, password, login_btn = self.find_login_elements()
        
        username.send_keys('370.768.438-54')
        password.send_keys('@Leon02023091')
        login_btn.click()
        
        time.sleep(5)
        
    #def close(self):
    #    if self.driver:
    #        self.driver.quit()

def main():
    login = Login()
    
    try:
        login.ping()
        login.setup_driver()
        login.navigate()
        
        # Exemplo de uso:
        # scraper.login("seu_usuario", "sua_senha")
        
        print(f"Página carregada: {login.driver.title}")
        
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        pass
        #scraper.close()

if __name__ == "__main__":
    main()