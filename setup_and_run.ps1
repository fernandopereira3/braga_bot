# Script PowerShell para instalar dependências e executar check.py em modo oculto
# Execução: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Depois: .\setup_and_run.ps1

# Configurações
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

# Função para verificar se Python está instalado
function Test-Python {
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "❌ Python não encontrado" -ForegroundColor Red
        return $false
    }
}

# Função para instalar dependências
function Install-Dependencies {
    Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
    
    if (Test-Path "requirements.txt") {
        try {
            python -m pip install --upgrade pip
            python -m pip install -r requirements.txt
            Write-Host "✅ Dependências instaladas com sucesso" -ForegroundColor Green
        } catch {
            Write-Host "❌ Erro ao instalar dependências: $_" -ForegroundColor Red
            exit 1
        }
    } else {
        # Instala dependências básicas se requirements.txt não existir
        try {
            python -m pip install requests
            Write-Host "✅ Dependência 'requests' instalada" -ForegroundColor Green
        } catch {
            Write-Host "❌ Erro ao instalar requests: $_" -ForegroundColor Red
            exit 1
        }
    }
}

# Função para executar check.py em modo oculto
function Start-HiddenMonitor {
    Write-Host "🚀 Iniciando monitoramento em modo oculto..." -ForegroundColor Cyan
    
    if (Test-Path "check.py") {
        try {
            # Executa Python em modo oculto (sem janela de console)
            $processInfo = New-Object System.Diagnostics.ProcessStartInfo
            $processInfo.FileName = "python"
            $processInfo.Arguments = "check.py"
            $processInfo.WorkingDirectory = $scriptDir
            $processInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
            $processInfo.CreateNoWindow = $true
            
            $process = [System.Diagnostics.Process]::Start($processInfo)
            
            Write-Host "✅ Monitor iniciado em background (PID: $($process.Id))" -ForegroundColor Green
            Write-Host "📱 O script enviará notificações quando o site ficar online" -ForegroundColor Info
            Write-Host "⏹️  Para parar: taskkill /PID $($process.Id) /F" -ForegroundColor Yellow
            
        } catch {
            Write-Host "❌ Erro ao iniciar monitor: $_" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "❌ Arquivo check.py não encontrado" -ForegroundColor Red
        exit 1
    }
}

# Script principal
Write-Host "🔧 Configurando ambiente..." -ForegroundColor Magenta

# Verifica Python
if (-not (Test-Python)) {
    Write-Host "Por favor, instale o Python primeiro: https://python.org/downloads" -ForegroundColor Red
    exit 1
}

# Instala dependências
Install-Dependencies

# Executa monitor em modo oculto
Start-HiddenMonitor

Write-Host "🎉 Configuração concluída!" -ForegroundColor Green
Write-Host "O monitor está rodando em background e enviará notificações." -ForegroundColor Info