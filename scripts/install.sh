#!/bin/bash
# ============================================================
# GitClonePro - Installation Script
# ============================================================
# This script installs GitClonePro from source or PyPI
# 
# Usage:
#   ./install.sh              # Install from source
#   ./install.sh --pypi       # Install from PyPI
#   ./install.sh --dev        # Install in development mode
#   ./install.sh --help       # Show help
# ============================================================

set -e

# ==================== COLOR CODES ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# ==================== FUNCTIONS ====================
print_header() {
    echo -e "\n${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} ${CYAN}GitClonePro - Installation Script${NC}                           ${BLUE}║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ ${1}${NC}"
}

print_error() {
    echo -e "${RED}❌ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  ${1}${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  ${1}${NC}"
}

print_section() {
    echo -e "\n${CYAN}▶ ${1}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ==================== CHECK DEPENDENCIES ====================
check_dependencies() {
    print_section "Checking Dependencies"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found!"
        print_info "Please install Python 3.6 or higher:"
        echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
        echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
        echo "  macOS:         brew install python3"
        echo "  Windows:       https://www.python.org/downloads/"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python found: $PYTHON_VERSION"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_warning "pip3 not found. Installing..."
        python3 -m ensurepip --upgrade || {
            print_error "Failed to install pip"
            exit 1
        }
    fi
    print_success "pip found: $(pip3 --version | awk '{print $2}')"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_warning "Git not found!"
        print_info "Git is required for cloning repositories."
        print_info "Please install Git:"
        echo "  Ubuntu/Debian: sudo apt-get install git"
        echo "  CentOS/RHEL:   sudo yum install git"
        echo "  macOS:         brew install git"
        echo "  Windows:       https://git-scm.com/download/win"
        read -p "Continue without Git? (y/N) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        GIT_VERSION=$(git --version | awk '{print $3}')
        print_success "Git found: $GIT_VERSION"
    fi
    
    # Check Python version
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 6 ]]; then
        print_error "Python 3.6+ required. Found: $PYTHON_VERSION"
        exit 1
    fi
}

# ==================== INSTALLATION METHODS ====================
install_from_source() {
    print_section "Installing from Source"
    
    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    print_info "Project directory: $PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # Check if setup.py exists
    if [[ ! -f "setup.py" ]]; then
        print_error "setup.py not found in $PROJECT_DIR"
        exit 1
    fi
    
    # Install in development mode
    print_info "Installing in development mode..."
    pip3 install -e . || {
        print_error "Installation failed!"
        exit 1
    }
    
    print_success "GitClonePro installed from source!"
}

install_from_pypi() {
    print_section "Installing from PyPI"
    
    print_info "Installing GitClonePro from PyPI..."
    pip3 install gitclonepro || {
        print_error "Installation failed!"
        print_info "Try upgrading pip: pip3 install --upgrade pip"
        exit 1
    }
    
    print_success "GitClonePro installed from PyPI!"
}

install_dev_mode() {
    print_section "Installing in Development Mode"
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    cd "$PROJECT_DIR"
    
    print_info "Installing with development dependencies..."
    pip3 install -e ".[dev]" || {
        print_error "Installation failed!"
        exit 1
    }
    
    print_success "Development mode installed!"
    print_info "Available development commands:"
    echo "  pytest tests/           - Run tests"
    echo "  pytest tests/ --cov=gitclone - Run tests with coverage"
    echo "  black gitclone/         - Format code"
    echo "  flake8 gitclone/        - Lint code"
    echo "  mypy gitclone/          - Type check"
}

install_with_docker() {
    print_section "Installing with Docker"
    
    print_info "Building Docker image..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    cd "$PROJECT_DIR"
    
    # Check if Dockerfile exists
    if [[ ! -f "Dockerfile" ]]; then
        print_warning "Dockerfile not found. Creating one..."
        cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy source
COPY . .

# Install package
RUN pip install -e .

# Entry point
ENTRYPOINT ["gitclone"]
CMD ["--help"]
EOF
    fi
    
    docker build -t gitclonepro:latest . || {
        print_error "Docker build failed!"
        exit 1
    }
    
    print_success "Docker image built successfully!"
    print_info "Run with: docker run --rm gitclonepro:latest --help"
}

# ==================== POST-INSTALLATION ====================
post_install() {
    print_section "Post-Installation Setup"
    
    # Check if gitclone is available
    if command -v gitclone &> /dev/null; then
        print_success "gitclone command is available"
        VERSION=$(gitclone --version 2>/dev/null || echo "unknown")
        print_info "Version: $VERSION"
    else
        print_warning "gitclone command not found in PATH"
        print_info "Try running: pip3 install -e . (from source directory)"
    fi
    
    # Create default config
    CONFIG_DIR="$HOME/.config/gitclone"
    CONFIG_FILE="$CONFIG_DIR/config.yaml"
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        print_info "Creating default configuration..."
        mkdir -p "$CONFIG_DIR"
        cat > "$CONFIG_FILE" << 'EOF'
# GitClonePro Configuration
# Generated by install script

# GitHub Personal Access Token (optional)
# Generate at: https://github.com/settings/tokens
github_token: ""

# Default clone directory
clone_dir: "~/git_clones"

# Default branch
default_branch: "main"

# Retry settings
retries: 3
threads: 4
timeout: 30

# Output
verbose: true

# SSH
use_ssh: false
EOF
        print_success "Created config: $CONFIG_FILE"
    else
        print_info "Config already exists: $CONFIG_FILE"
    fi
    
    # Check for GitHub token
    if [[ -z "$GITHUB_TOKEN" ]]; then
        print_warning "GITHUB_TOKEN environment variable not set"
        print_info "Set it with: export GITHUB_TOKEN=ghp_xxxxxxxxxxxx"
    fi
}

# ==================== SHOW HELP ====================
show_help() {
    echo "GitClonePro Installation Script"
    echo ""
    echo "Usage: ./install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --pypi          Install from PyPI (default: source)"
    echo "  --dev           Install in development mode with dev dependencies"
    echo "  --docker        Install and build Docker image"
    echo "  --help, -h      Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./install.sh              # Install from source"
    echo "  ./install.sh --pypi       # Install from PyPI"
    echo "  ./install.sh --dev        # Install in development mode"
    echo "  ./install.sh --docker     # Build Docker image"
    echo ""
}

# ==================== MAIN ====================
main() {
    print_header
    
    # Parse arguments
    INSTALL_METHOD="source"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --pypi)
                INSTALL_METHOD="pypi"
                shift
                ;;
            --dev)
                INSTALL_METHOD="dev"
                shift
                ;;
            --docker)
                INSTALL_METHOD="docker"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Check dependencies
    check_dependencies
    
    # Install based on method
    case $INSTALL_METHOD in
        source)
            install_from_source
            ;;
        pypi)
            install_from_pypi
            ;;
        dev)
            install_dev_mode
            ;;
        docker)
            install_with_docker
            ;;
    esac
    
    # Post-installation
    post_install
    
    # Success message
    echo ""
    print_section "Installation Complete!"
    echo -e "${GREEN}🎉 GitClonePro has been successfully installed!${NC}"
    echo ""
    echo -e "${CYAN}Quick Start:${NC}"
    echo "  gitclone https://github.com/octocat/Hello-World"
    echo "  gitclone --help"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  # Clone a repository"
    echo "  gitclone https://github.com/octocat/Hello-World"
    echo ""
    echo "  # Sparse clone (only specific files)"
    echo "  gitclone https://github.com/facebook/react --sparse src/ README.md"
    echo ""
    echo "  # Batch clone all repos from a user"
    echo "  gitclone --owner octocat --type public --threads 4"
    echo ""
    echo -e "${CYAN}Documentation:${NC}"
    echo "  https://github.com/yourusername/GitClonePro"
    echo ""
    echo -e "${GREEN}Happy cloning! 🚀${NC}"
}

# ==================== RUN MAIN ====================
main "$@"