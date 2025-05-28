#!/bin/bash

# Script d'installation automatique pour Agriculture Cameroun
# Usage: curl -sSL https://raw.githubusercontent.com/Nameless0l/agriculture-cameroun/main/setup.sh | bash

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
B    echo "📞 Support:"
    echo "- GitHub Issues: https://github.com/Nameless0l/agriculture-cameroun/issues"
    echo "- Email: wwwmbassiloic@gmail.com"
    echo "- Portfolio: http://mbassiloic.tech/"='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
print_header() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier l'OS
check_os() {
    print_header "🔍 Vérification du système d'exploitation..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Linux détecté"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "macOS détecté"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        print_success "Windows détecté"
    else
        print_error "Système d'exploitation non supporté: $OSTYPE"
        exit 1
    fi
}

# Vérifier Python
check_python() {
    print_header "🐍 Vérification de Python..."
    
    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD="python3.12"
        print_success "Python 3.12 trouvé"
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [[ $MAJOR -eq 3 && $MINOR -ge 12 ]]; then
            PYTHON_CMD="python3"
            print_success "Python $PYTHON_VERSION trouvé (compatible)"
        else
            print_error "Python 3.12+ requis, trouvé: $PYTHON_VERSION"
            install_python
        fi
    else
        print_error "Python non trouvé"
        install_python
    fi
}

# Installer Python
install_python() {
    print_header "📦 Installation de Python..."
    
    case $OS in
        "linux")
            if command -v apt &> /dev/null; then
                sudo apt update
                sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip
            elif command -v yum &> /dev/null; then
                sudo yum install -y python312 python312-devel python312-pip
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y python3.12 python3.12-devel python3.12-pip
            else
                print_error "Gestionnaire de paquets non supporté"
                exit 1
            fi
            PYTHON_CMD="python3.12"
            ;;
        "macos")
            if command -v brew &> /dev/null; then
                brew install python@3.12
                PYTHON_CMD="python3.12"
            else
                print_error "Homebrew requis pour installer Python sur macOS"
                print_warning "Installez Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            ;;
        "windows")
            print_error "Installation automatique de Python non supportée sur Windows"
            print_warning "Téléchargez Python depuis: https://python.org/downloads/"
            exit 1
            ;;
    esac
    
    print_success "Python installé avec succès"
}

# Vérifier Poetry
check_poetry() {
    print_header "📚 Vérification de Poetry..."
    
    if command -v poetry &> /dev/null; then
        print_success "Poetry trouvé"
    else
        print_warning "Poetry non trouvé, installation..."
        install_poetry
    fi
}

# Installer Poetry
install_poetry() {
    print_header "📦 Installation de Poetry..."
    
    curl -sSL https://install.python-poetry.org | $PYTHON_CMD -
    
    # Ajouter Poetry au PATH
    export PATH="$HOME/.local/bin:$PATH"
    
    if command -v poetry &> /dev/null; then
        print_success "Poetry installé avec succès"
    else
        print_error "Échec de l'installation de Poetry"
        print_warning "Ajoutez manuellement ~/.local/bin au PATH"
        exit 1
    fi
}

# Vérifier Git
check_git() {
    print_header "🔄 Vérification de Git..."
    
    if command -v git &> /dev/null; then
        print_success "Git trouvé"
    else
        print_warning "Git non trouvé, installation..."
        install_git
    fi
}

# Installer Git
install_git() {
    case $OS in
        "linux")
            if command -v apt &> /dev/null; then
                sudo apt install -y git
            elif command -v yum &> /dev/null; then
                sudo yum install -y git
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y git
            fi
            ;;
        "macos")
            if command -v brew &> /dev/null; then
                brew install git
            else
                xcode-select --install
            fi
            ;;
        "windows")
            print_error "Installation automatique de Git non supportée sur Windows"
            print_warning "Téléchargez Git depuis: https://git-scm.com/download/win"
            exit 1
            ;;
    esac
    
    print_success "Git installé avec succès"
}

# Cloner le projet
clone_project() {
    print_header "📥 Clonage du projet..."
    
    PROJECT_DIR="agriculture-cameroun"
    
    if [[ -d "$PROJECT_DIR" ]]; then
        print_warning "Le dossier $PROJECT_DIR existe déjà"
        read -p "Voulez-vous le supprimer et recommencer ? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$PROJECT_DIR"
        else
            print_error "Installation annulée"
            exit 1
        fi
    fi
    
    git clone https://github.com/Nameless0l/agriculture-cameroun.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    print_success "Projet cloné avec succès"
}

# Installer les dépendances
install_dependencies() {
    print_header "📦 Installation des dépendances..."
    
    poetry install
    
    print_success "Dépendances installées avec succès"
}

# Configurer l'environnement
setup_environment() {
    print_header "⚙️  Configuration de l'environnement..."
    
    if [[ ! -f ".env" ]]; then
        cp .env.example .env
        print_success "Fichier .env créé"
        
        print_warning "⚠️  IMPORTANT: Vous devez configurer votre clé API Gemini"
        echo "1. Allez sur https://aistudio.google.com/"
        echo "2. Créez une clé API"
        echo "3. Modifiez le fichier .env et remplacez 'your_gemini_api_key_here'"
        echo ""
        read -p "Appuyez sur Entrée pour continuer..."
    else
        print_warning "Fichier .env existe déjà"
    fi
}

# Tester l'installation
test_installation() {
    print_header "🧪 Test de l'installation..."
    
    if poetry run python -c "import agriculture_cameroun; print('Import réussi')" &> /dev/null; then
        print_success "Import du module réussi"
    else
        print_error "Échec de l'import du module"
        return 1
    fi
    
    # Vérifier la configuration
    if grep -q "your_gemini_api_key_here" .env; then
        print_warning "Clé API Gemini non configurée"
        return 1
    else
        print_success "Configuration semble correcte"
    fi
    
    return 0
}

# Afficher les instructions finales
show_final_instructions() {
    print_header "🎉 Installation terminée !"
    
    echo ""
    echo "📋 Prochaines étapes:"
    echo "1. cd agriculture-cameroun"
    echo "2. Modifier le fichier .env avec votre clé API Gemini"
    echo "3. poetry shell"
    echo "4. adk serve . --port 8080"
    echo "5. Ouvrir http://localhost:8080 dans votre navigateur"
    echo ""
    echo "📖 Documentation:"
    echo "- Guide complet: README.md"
    echo "- Installation détaillée: INSTALLATION.md"
    echo "- Démarrage rapide: QUICKSTART.md"
    echo ""
    echo "🆘 Support:"
    echo "- GitHub Issues: https://github.com/Nameless0l/agriculture-cameroun/issues"
    echo "- Email: team@agriculture-cm.com"
    echo ""
    print_success "Bon agriculture avec l'IA ! 🌱"
}

# Fonction principale
main() {
    clear
    echo "🌱 Agriculture Cameroun - Installation Automatique 🌱"
    echo "=================================================="
    echo ""
    
    check_os
    check_python
    check_poetry
    check_git
    clone_project
    install_dependencies
    setup_environment
    
    if test_installation; then
        show_final_instructions
    else
        print_error "Installation incomplète - vérifiez la configuration"
        echo "Consultez INSTALLATION.md pour l'installation manuelle"
    fi
}

# Exécuter le script principal
main "$@"
