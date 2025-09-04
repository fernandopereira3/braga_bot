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
                ps_script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                $notification = New-Object System.Windows.Forms.NotifyIcon
                $notification.Icon = [System.Drawing.SystemIcons]::Information
                $notification.BalloonTipTitle = "Site Monitor"
                $notification.BalloonTipText = "{message}"
                $notification.Visible = $true
                $notification.ShowBalloonTip(5000)
                Start-Sleep -Seconds 6
                $notification.Dispose()
                '''
                subprocess.run(["powershell", "-Command", ps_script], check=True)
        except:
            pass

    def ask_user_continue(self):
        """Pergunta ao usuário se deseja continuar"""
        try:
            response = (
                input("\n🌐 Site está online! Deseja continuar monitorando? (s/n): ")
                .lower()
                .strip()
            )
            return response in ["s", "sim", "y", "yes", ""]
        except KeyboardInterrupt:
            return False

    def monitor(self, interval=10):
        """Monitora conectividade"""
        try:
            while True:
                if self.is_online():
                    self.notify("Site está online!")

                    # Pergunta se o usuário quer continuar
                    if not self.ask_user_continue():
                        break

                time.sleep(interval)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    checker = ConnectivityChecker()
    checker.monitor()
