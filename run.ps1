<#
.SYNOPSIS
    Script de Automatización PowerShell para el Laboratorio Multi-Paradigma de Bases de Datos.
.DESCRIPTION
    Facilita el despliegue, verificación, sembrado de datos y apertura de dashboards.
.EXAMPLE
    .\run.ps1 up
    .\run.ps1 seed
    .\run.ps1 open-dashboards
    .\run.ps1 clean
#>

param(
    [ValidateSet("up", "down", "restart", "status", "seed", "open-dashboards", "clean", "help")]
    [string]$Action = "help"
)

$ErrorActionPreference = "Stop"

function Show-Header {
    Write-Host ""
    Write-Host "==========================================================================" -ForegroundColor Cyan
    Write-Host "       LABORATORIO MULTI-PARADIGMA DE BASES DE DATOS - WINDOWS / DEVOPS   " -ForegroundColor Yellow
    Write-Host "==========================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Dashboards {
    Write-Host "`n[+] Dashboards e Interfaces Web de Gestión:" -ForegroundColor Green
    Write-Host "  1. PostgreSQL (Adminer UI):   http://localhost:8080" -ForegroundColor White
    Write-Host "     - Servidor: postgres | Usuario: postgres | Contraseña: postgrespassword | Base: lab_sql" -ForegroundColor DarkGray
    Write-Host "  2. MongoDB (Mongo Express):   http://localhost:8081" -ForegroundColor White
    Write-Host "     - Acceso directo sin autenticación básica para desarrollo local" -ForegroundColor DarkGray
    Write-Host "  3. Redis (RedisInsight):      http://localhost:5540" -ForegroundColor White
    Write-Host "     - Host: redis o host.docker.internal | Puerto: 6379 | Password: redispassword" -ForegroundColor DarkGray
    Write-Host "  4. Neo4j (Neo4j Browser UI):  http://localhost:7474" -ForegroundColor White
    Write-Host "     - Usuario: neo4j | Contraseña: neo4jpassword" -ForegroundColor DarkGray
    Write-Host "  5. InfluxDB (Influx Web UI):  http://localhost:8086" -ForegroundColor White
    Write-Host "     - Usuario: influxadmin | Contraseña: influxpassword123 | Org: devops-lab" -ForegroundColor DarkGray
    Write-Host ""
}

Show-Header

switch ($Action) {
    "up" {
        Write-Host "[*] Iniciando servicios de bases de datos y dashboards en segundo plano..." -ForegroundColor Cyan
        docker compose up -d
        Write-Host "`n[✔] Contenedores desplegados. Esperando sincronización inicial (10s)..." -ForegroundColor Green
        Start-Sleep -Seconds 10
        docker compose ps
        Show-Dashboards
    }

    "down" {
        Write-Host "[*] Deteniendo todos los contenedores..." -ForegroundColor Yellow
        docker compose down
        Write-Host "[✔] Contenedores detenidos correctamente." -ForegroundColor Green
    }

    "restart" {
        Write-Host "[*] Reiniciando contenedores..." -ForegroundColor Yellow
        docker compose restart
        docker compose ps
    }

    "status" {
        Write-Host "[*] Estado actual de los contenedores:" -ForegroundColor Cyan
        docker compose ps
        Show-Dashboards
    }

    "seed" {
        Write-Host "[*] Verificando entorno Python y ejecutando sembrado de datos..." -ForegroundColor Cyan
        $pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
        if (-not (Test-Path $pythonExe)) {
            Write-Host "[!] Entorno virtual no encontrado. Usando python del sistema..." -ForegroundColor Yellow
            $pythonExe = "python"
        }
        & $pythonExe "$PSScriptRoot\seed_and_demo.py"
    }

    "open-dashboards" {
        Write-Host "[*] Abriendo interfaces web en el navegador por defecto..." -ForegroundColor Cyan
        Start-Process "http://localhost:8080"  # Adminer
        Start-Process "http://localhost:8081"  # Mongo Express
        Start-Process "http://localhost:5540"  # RedisInsight
        Start-Process "http://localhost:7474"  # Neo4j Browser
        Start-Process "http://localhost:8086"  # InfluxDB
        Write-Host "[✔] Pestañas abiertas en el navegador." -ForegroundColor Green
    }

    "clean" {
        Write-Host "[!] ADVERTENCIA: Se detendrán los contenedores y se eliminará la carpeta local ./data" -ForegroundColor Red
        $confirm = Read-Host "¿Deseas continuar? (S/N)"
        if ($confirm -eq "S" -or $confirm -eq "s") {
            docker compose down -v
            if (Test-Path "$PSScriptRoot\data") {
                Remove-Item -Recurse -Force "$PSScriptRoot\data"
                Write-Host "[✔] Volúmenes locales ./data eliminados con éxito." -ForegroundColor Green
            }
        } else {
            Write-Host "Operación cancelada." -ForegroundColor Yellow
        }
    }

    "help" {
        Write-Host "Uso: .\run.ps1 [ACCION]" -ForegroundColor White
        Write-Host "Acciones disponibles:" -ForegroundColor Yellow
        Write-Host "  up               Levanta todos los motores e interfaces en Docker"
        Write-Host "  status           Muestra el estado de salud de cada contenedor y las URLs"
        Write-Host "  seed             Ejecuta el script de prueba y sembrado en Python"
        Write-Host "  open-dashboards  Abre los 5 paneles web en el navegador automáticamente"
        Write-Host "  down             Detiene los contenedores sin borrar datos"
        Write-Host "  clean            Detiene contenedores y limpia volúmenes locales persistidos"
        Write-Host "  help             Muestra esta ayuda"
        Write-Host ""
    }
}
