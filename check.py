import requests
import time
import subprocess
import sys


class ConnectivityChecker:
    def __init__(self, url):
        self.URL = url

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

    def wait_and_execute(self, script_path="app_main.py"):
        """Aguarda o site ficar online e executa o script principal"""
        print("🔍 Verificando conectividade...")

        if self.check_connectivity():
            print("✅ Site já está online! Executando app_main...")
            self._execute_script(script_path)
        else:
            print("⏳ Site offline. Aguardando ficar online...")
            self.wait_for_site()
            print("🚀 Executando app_main...")
            self._execute_script(script_path)

    def _execute_script(self, script_path):
        """Executa o script Python especificado"""
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                check=True,
            )
            print("✅ Script executado com sucesso!")
            if result.stdout:
                print("Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao executar o script: {e}")
            if e.stderr:
                print("Erro:", e.stderr)
        except FileNotFoundError:
            print(f"❌ Arquivo {script_path} não encontrado!")


# Função para uso direto
def monitor_and_execute(
    url="http://ead.cecp.sp.gov.br/login/index.php", script="app_main.py"
):
    """Monitora o site e executa o script quando estiver online"""
    checker = ConnectivityChecker(url)
    checker.wait_and_execute(script)


if __name__ == "__main__":
    # Executa o monitoramento se o arquivo for chamado diretamente
    monitor_and_execute()
