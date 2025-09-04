import requests
import time
import subprocess
import platform


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
        self._send_notification("AVISO!", "Cecp está online e acessível! CORRE!")

    def monitor_site(self):
        """Monitora o site e envia notificações quando ficar online"""
        print("🔍 Verificando conectividade...")

        if self.check_connectivity():
            print("✅ Site já está online!")
            self._send_notification("AVISO!", "Cecp está online e acessível! CORRE")
        else:
            print("⏳ Site offline. Monitorando...")
            self.wait_for_site()

    def _send_notification(self, title, message):
        """Envia notificação push do sistema operacional"""
        try:
            system = platform.system().lower()

            if system == "darwin":  # macOS
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        f'display notification "{message}" with title "{title}"',
                    ],
                    check=True,
                )

            elif system == "linux":
                # Verifica se notify-send está disponível
                subprocess.run(["notify-send", title, message], check=True)

            elif system == "windows":
                # Usa PowerShell para Windows 10/11
                ps_script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                $notification = New-Object System.Windows.Forms.NotifyIcon
                $notification.Icon = [System.Drawing.SystemIcons]::Information
                $notification.BalloonTipTitle = "{title}"
                $notification.BalloonTipText = "{message}"
                $notification.Visible = $true
                $notification.ShowBalloonTip(5000)
                Start-Sleep -Seconds 6
                $notification.Dispose()
                '''
                subprocess.run(["powershell", "-Command", ps_script], check=True)

            else:
                print(f"⚠️ Notificações não suportadas para {system}")

        except subprocess.CalledProcessError:
            print("⚠️ Falha ao enviar notificação push")
        except Exception as e:
            print(f"⚠️ Erro na notificação: {e}")


# Função para uso direto
def monitor_connectivity(url="http://ead.cecp.sp.gov.br/login/index.php"):
    """Monitora o site e envia notificações quando estiver online"""
    checker = ConnectivityChecker(url)
    checker.monitor_site()


if __name__ == "__main__":
    # Executa o monitoramento se o arquivo for chamado diretamente
    monitor_connectivity()
