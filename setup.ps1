# Script d'installation automatique pour Agriculture Cameroun (Windows)
# Usage: iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/Nameless0l/agriculture-cameroun/main/setup.ps1'))

# Vérification des privilèges administrateur
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Ce script nécessite des privilèges administrateur" -ForegroundColor Red
    Write-Host "Relancez PowerShell en tant qu'administrateur" -ForegroundColor Yellow
    exit 1
}

# Couleurs pour les messages
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }

Write-Host "Agriculture Cameroun - Installation Automatique (Windows)" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Vérifier si Chocolatey est installé
Write-Info "Vérification de Chocolatey..."
if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Success "Chocolatey trouvé"
} else {
    Write-Warning "Chocolatey non trouvé, installation..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    Write-Success "Chocolatey installé"
}

# Vérifier Python
Write-Info "Vérification de Python..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.1[2-9]") {
        Write-Success "Python $($pythonVersion.Split()[1]) trouvé (compatible)"
        $pythonCmd = "python"
    } else {
        throw "Version incompatible"
    }
} catch {
    Write-Warning "Python 3.12+ non trouvé, installation..."
    choco install python312 -y
    refreshenv
    $pythonCmd = "python"
    Write-Success "Python installé"
}

# Vérifier Git
Write-Info "Vérification de Git..."
if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Success "Git trouvé"
} else {
    Write-Warning "Git non trouvé, installation..."
    choco install git -y
    refreshenv
    Write-Success "Git installé"
}

# Installer Poetry
Write-Info "Vérification de Poetry..."
if (Get-Command poetry -ErrorAction SilentlyContinue) {
    Write-Success "Poetry trouvé"
} else {
    Write-Warning "Poetry non trouvé, installation..."
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    
    # Ajouter Poetry au PATH
    $poetryPath = "$env:APPDATA\Python\Scripts"
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentPath -notlike "*$poetryPath*") {
        [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$poetryPath", "User")
    }
    
    # Recharger la session
    $env:PATH = "$env:PATH;$poetryPath"
    Write-Success "Poetry installé"
}

# Cloner le projet
Write-Info "Clonage du projet..."
$projectDir = "agriculture-cameroun"

if (Test-Path $projectDir) {
    Write-Warning "Le dossier $projectDir existe déjà"
    $response = Read-Host "Voulez-vous le supprimer et recommencer ? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Remove-Item -Recurse -Force $projectDir
    } else {
        Write-Error "Installation annulée"
        exit 1
    }
}

git clone https://github.com/Nameless0l/agriculture-cameroun.git $projectDir
Set-Location $projectDir
Write-Success "Projet cloné avec succès"

# Installer les dépendances
Write-Info "Installation des dépendances..."
poetry install
Write-Success "Dépendances installées avec succès"

# Configurer l'environnement
Write-Info "Configuration de l'environnement..."
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Success "Fichier .env créé"
    
    Write-Warning "⚠️  IMPORTANT: Vous devez configurer votre clé API Gemini"
    Write-Host "1. Allez sur https://aistudio.google.com/" -ForegroundColor Cyan
    Write-Host "2. Créez une clé API" -ForegroundColor Cyan
    Write-Host "3. Modifiez le fichier .env et remplacez 'your_gemini_api_key_here'" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Appuyez sur Entrée pour continuer..."
} else {
    Write-Warning "Fichier .env existe déjà"
}

# Tester l'installation
Write-Info "Test de l'installation..."
try {
    poetry run python -c "import agriculture_cameroun; print('Import réussi')" 2>$null
    Write-Success "Import du module réussi"
    
    # Vérifier la configuration
    $envContent = Get-Content ".env"
    if ($envContent -match "your_gemini_api_key_here") {
        Write-Warning "Clé API Gemini non configurée"
        $testPassed = $false
    } else {
        Write-Success "Configuration semble correcte"
        $testPassed = $true
    }
} catch {
    Write-Error "Échec de l'import du module"
    $testPassed = $false
}

# Instructions finales
Write-Host ""
Write-Host "🎉 Installation terminée !" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Prochaines étapes:" -ForegroundColor Cyan
Write-Host "1. Modifier le fichier .env avec votre clé API Gemini" -ForegroundColor White
Write-Host "2. poetry shell" -ForegroundColor White
Write-Host "3. adk serve . --port 8080" -ForegroundColor White
Write-Host "4. Ouvrir http://localhost:8080 dans votre navigateur" -ForegroundColor White
Write-Host ""
Write-Host "📖 Documentation:" -ForegroundColor Cyan
Write-Host "- Guide complet: README.md" -ForegroundColor White
Write-Host "- Installation détaillée: INSTALLATION.md" -ForegroundColor White
Write-Host "- Démarrage rapide: QUICKSTART.md" -ForegroundColor White
Write-Host ""
Write-Host "🆘 Support:" -ForegroundColor Cyan
Write-Host "- GitHub Issues: https://github.com/Nameless0l/agriculture-cameroun/issues" -ForegroundColor White
Write-Host "- Email: wwwmbassiloic@gmail.com" -ForegroundColor White
Write-Host "- Portfolio: http://mbassiloic.tech/" -ForegroundColor White
Write-Host ""

if ($testPassed) {
    Write-Success "Bon agriculture avec l'IA ! 🌱"
} else {
    Write-Error "Installation incomplète - vérifiez la configuration"
    Write-Host "Consultez INSTALLATION.md pour l'installation manuelle" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
