import requests
import time
import subprocess
import platform


class ConnectivityChecker:
    def __init__(self, url="http://ead.cecp.sp.gov.br/login/index.php"):
        self.url = url

    def is_online(self):
        """Verifica se o site está online"""
        try:
            response = requests.get(self.url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def notify(self, message):
        """Envia notificação do sistema"""
        try:
            system = platform.system().lower()
            if system == "darwin":
                subprocess.run(
                    ["osascript", "-e", f'display notification "{message}"'], check=True
                )
            elif system == "linux":
                subprocess.run(["notify-send", message], check=True)
            elif system == "windows":
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        f'[System.Windows.Forms.MessageBox]::Show("{message}")',
                    ],
                    check=True,
                )
        except:
            pass

    def monitor(self, interval=10):
        """Monitora conectividade"""
        try:
            while True:
                if self.is_online():
                    self.notify("Site está online!")

                time.sleep(interval)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    checker = ConnectivityChecker()
    checker.monitor()
