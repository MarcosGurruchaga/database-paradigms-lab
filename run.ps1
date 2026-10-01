<#
.SYNOPSIS
    Script de Automatizacion PowerShell para el Laboratorio Multi-Paradigma de Bases de Datos.
.DESCRIPTION
    Facilita el despliegue, verificacion, sembrado de datos y apertura de dashboards.
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
    Write-Host ""
    Write-Host "[+] Dashboards e Interfaces Web de Gestion:" -ForegroundColor Green
    Write-Host "  1. PostgreSQL (Adminer UI):   http://localhost:8080" -ForegroundColor White
    Write-Host "     - Servidor: postgres | Usuario: postgres | Clave: postgrespassword | Base: lab_sql" -ForegroundColor DarkGray
    Write-Host "  2. MongoDB (Mongo Express):   http://localhost:8081" -ForegroundColor White
    Write-Host "     - Acceso directo sin autenticacion basica para desarrollo local" -ForegroundColor DarkGray
    Write-Host "  3. Redis (RedisInsight):      http://localhost:5540" -ForegroundColor White
    Write-Host "     - Host: redis o host.docker.internal | Puerto: 6379 | Password: redispassword" -ForegroundColor DarkGray
    Write-Host "  4. Neo4j (Neo4j Browser UI):  http://localhost:7474" -ForegroundColor White
    Write-Host "     - Usuario: neo4j | Contrasena: neo4jpassword" -ForegroundColor DarkGray
    Write-Host "  5. InfluxDB (Influx Web UI):  http://localhost:8086" -ForegroundColor White
    Write-Host "     - Usuario: influxadmin | Contrasena: influxpassword123 | Org: devops-lab" -ForegroundColor DarkGray
    Write-Host ""
}

Show-Header

switch ($Action) {
    "up" {
        Write-Host "[*] Iniciando servicios de bases de datos y dashboards en segundo plano..." -ForegroundColor Cyan
        docker compose up -d
        Write-Host ""
        Write-Host "[OK] Contenedores desplegados. Esperando sincronizacion inicial (10s)..." -ForegroundColor Green
        Start-Sleep -Seconds 10
        docker compose ps
        Show-Dashboards
    }

    "down" {
        Write-Host "[*] Deteniendo todos los contenedores..." -ForegroundColor Yellow
        docker compose down
        Write-Host "[OK] Contenedores detenidos correctamente." -ForegroundColor Green
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
        Start-Process "http://localhost:8080"
        Start-Process "http://localhost:8081"
        Start-Process "http://localhost:5540"
        Start-Process "http://localhost:7474"
        Start-Process "http://localhost:8086"
        Write-Host "[OK] Pestanas abiertas en el navegador." -ForegroundColor Green
    }

    "clean" {
        Write-Host "[!] ADVERTENCIA: Se detendran los contenedores y se eliminara la carpeta local ./data" -ForegroundColor Red
        $confirm = Read-Host "Deseas continuar? (S/N)"
        if ($confirm -eq "S" -or $confirm -eq "s") {
            docker compose down -v
            if (Test-Path "$PSScriptRoot\data") {
                Remove-Item -Recurse -Force "$PSScriptRoot\data"
                Write-Host "[OK] Volumenes locales ./data eliminados con exito." -ForegroundColor Green
            }
        } else {
            Write-Host "Operacion cancelada." -ForegroundColor Yellow
        }
    }

    "help" {
        Write-Host "Uso: .\run.ps1 [ACCION]" -ForegroundColor White
        Write-Host "Acciones disponibles:" -ForegroundColor Yellow
        Write-Host "  up               Levanta todos los motores e interfaces en Docker"
        Write-Host "  status           Muestra el estado de salud de cada contenedor y las URLs"
        Write-Host "  seed             Ejecuta el script de prueba y sembrado en Python"
        Write-Host "  open-dashboards  Abre los 5 paneles web en el navegador automaticamente"
        Write-Host "  down             Detiene los contenedores sin borrar datos"
        Write-Host "  clean            Detiene contenedores y limpia volumenes locales persistidos"
        Write-Host "  help             Muestra esta ayuda"
        Write-Host ""
    }
}
