#!/bin/bash
# ============================================================
# GitClonePro - Update Script
# ============================================================
# This script updates GitClonePro to the latest version
# 
# Usage:
#   ./update.sh              # Update to latest version
#   ./update.sh --force      # Force update (reinstall)
#   ./update.sh --check      # Check for updates without installing
#   ./update.sh --help       # Show help
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
    echo -e "${BLUE}║${NC} ${CYAN}GitClonePro - Update Script${NC}                                 ${BLUE}║${NC}"
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

print_result() {
    echo -e "${WHITE}  ${1}:${NC} ${2}"
}

# ==================== CHECK CURRENT VERSION ====================
get_current_version() {
    if command -v gitclone &> /dev/null; then
        gitclone --version 2>/dev/null | awk '{print $2}' || echo "unknown"
    else
        echo "not-installed"
    fi
}

get_installed_location() {
    if command -v gitclone &> /dev/null; then
        which gitclone 2>/dev/null || echo "unknown"
    else
        echo "not-installed"
    fi
}

check_installation_type() {
    local location=$(get_installed_location)
    
    if [[ "$location" == "not-installed" ]]; then
        echo "none"
    elif [[ "$location" == *"site-packages"* ]] || [[ "$location" == *"dist-packages"* ]]; then
        echo "pip"
    elif [[ "$location" == *"bin"* ]] && [[ -d "$(dirname "$location")/../lib" ]]; then
        echo "pip"
    else
        echo "source"
    fi
}

# ==================== CHECK FOR UPDATES ====================
check_pypi_version() {
    print_info "Checking PyPI for latest version..."
    
    LATEST_VERSION=$(pip3 index versions gitclonepro 2>/dev/null | grep -oP 'Available versions: \K[^,]+' | head -1)
    
    if [[ -z "$LATEST_VERSION" ]]; then
        LATEST_VERSION=$(curl -s https://pypi.org/pypi/gitclonepro/json 2>/dev/null | grep -oP '"version":"\K[^"]+' | head -1)
    fi
    
    if [[ -z "$LATEST_VERSION" ]]; then
        print_warning "Could not check PyPI version"
        echo "unknown"
    else
        echo "$LATEST_VERSION"
    fi
}

check_github_version() {
    print_info "Checking GitHub for latest version..."
    
    LATEST_VERSION=$(curl -s https://api.github.com/repos/yourusername/GitClonePro/releases/latest 2>/dev/null | grep -oP '"tag_name": "\K[^"]+')
    
    if [[ -z "$LATEST_VERSION" ]]; then
        # Try using git
        if git ls-remote https://github.com/yourusername/GitClonePro.git refs/tags/* 2>/dev/null | grep -q .; then
            LATEST_VERSION=$(git ls-remote --tags https://github.com/yourusername/GitClonePro.git 2>/dev/null | grep -oP 'refs/tags/\K[^^{]+' | sort -V | tail -1)
        fi
    fi
    
    if [[ -z "$LATEST_VERSION" ]]; then
        print_warning "Could not check GitHub version"
        echo "unknown"
    else
        echo "$LATEST_VERSION"
    fi
}

# ==================== UPDATE METHODS ====================
update_from_pip() {
    print_section "Updating from PyPI"
    
    print_info "Current version: $CURRENT_VERSION"
    print_info "Latest version: $LATEST_VERSION"
    
    if [[ "$CURRENT_VERSION" == "$LATEST_VERSION" ]] && [[ "$FORCE" != "true" ]]; then
        print_success "You already have the latest version!"
        return 0
    fi
    
    print_info "Upgrading GitClonePro..."
    pip3 install --upgrade gitclonepro || {
        print_error "Update failed!"
        return 1
    }
    
    print_success "Update completed!"
}

update_from_source() {
    print_section "Updating from Source"
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    print_info "Project directory: $PROJECT_DIR"
    
    cd "$PROJECT_DIR"
    
    # Check if git repository
    if [[ ! -d ".git" ]]; then
        print_warning "Not a git repository. Pulling from GitHub..."
        git init
        git remote add origin https://github.com/yourusername/GitClonePro.git
        git fetch
        git checkout main || git checkout master
    fi
    
    # Get current commit
    CURRENT_COMMIT=$(git rev-parse HEAD 2>/dev/null | cut -c1-8)
    print_info "Current commit: $CURRENT_COMMIT"
    
    # Pull latest
    print_info "Pulling latest changes..."
    git pull origin main || git pull origin master || {
        print_error "Failed to pull latest changes"
        return 1
    }
    
    # Get new commit
    NEW_COMMIT=$(git rev-parse HEAD 2>/dev/null | cut -c1-8)
    print_info "New commit: $NEW_COMMIT"
    
    if [[ "$CURRENT_COMMIT" == "$NEW_COMMIT" ]] && [[ "$FORCE" != "true" ]]; then
        print_success "You already have the latest version!"
        return 0
    fi
    
    # Reinstall
    print_info "Reinstalling from source..."
    pip3 install -e . || {
        print_error "Reinstallation failed!"
        return 1
    }
    
    print_success "Update completed!"
}

update_from_docker() {
    print_section "Updating Docker Image"
    
    print_info "Pulling latest Docker image..."
    docker pull ghcr.io/yourusername/gitclonepro:latest || {
        print_error "Docker pull failed!"
        return 1
    }
    
    print_success "Docker image updated!"
}

# ==================== SHOW STATUS ====================
show_status() {
    print_section "Current Status"
    
    print_result "Version" "$CURRENT_VERSION"
    print_result "Location" "$INSTALL_LOCATION"
    print_result "Installation Type" "$INSTALL_TYPE"
    print_result "Latest Version" "$LATEST_VERSION"
    
    if [[ "$CURRENT_VERSION" != "not-installed" ]]; then
        if [[ "$CURRENT_VERSION" == "$LATEST_VERSION" ]]; then
            print_success "Up to date!"
        elif [[ "$LATEST_VERSION" != "unknown" ]]; then
            print_warning "Update available: $LATEST_VERSION"
            print_info "Run ./update.sh to update"
        fi
    else
        print_warning "GitClonePro is not installed"
        print_info "Run ./install.sh to install"
    fi
}

# ==================== SHOW HELP ====================
show_help() {
    echo "GitClonePro Update Script"
    echo ""
    echo "Usage: ./update.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --force, -f    Force update (reinstall even if up-to-date)"
    echo "  --check, -c    Check for updates without installing"
    echo "  --docker       Update Docker image"
    echo "  --help, -h     Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./update.sh              # Update to latest version"
    echo "  ./update.sh --force      # Force reinstall"
    echo "  ./update.sh --check      # Check for updates"
    echo "  ./update.sh --docker     # Update Docker image"
    echo ""
}

# ==================== MAIN ====================
main() {
    print_header
    
    # Default values
    FORCE="false"
    CHECK_ONLY="false"
    UPDATE_DOCKER="false"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force|-f)
                FORCE="true"
                shift
                ;;
            --check|-c)
                CHECK_ONLY="true"
                shift
                ;;
            --docker)
                UPDATE_DOCKER="true"
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
    
    # Get current information
    CURRENT_VERSION=$(get_current_version)
    INSTALL_LOCATION=$(get_installed_location)
    INSTALL_TYPE=$(check_installation_type)
    
    # Get latest versions
    LATEST_VERSION=$(check_pypi_version)
    LATEST_GITHUB=$(check_github_version)
    
    # Use GitHub version if PyPI check failed
    if [[ "$LATEST_VERSION" == "unknown" ]] && [[ "$LATEST_GITHUB" != "unknown" ]]; then
        LATEST_VERSION="$LATEST_GITHUB"
    fi
    
    # Show status
    show_status
    
    # Exit if check only
    if [[ "$CHECK_ONLY" == "true" ]]; then
        exit 0
    fi
    
    # Check if installed
    if [[ "$CURRENT_VERSION" == "not-installed" ]]; then
        print_error "GitClonePro is not installed!"
        print_info "Run ./install.sh to install"
        exit 1
    fi
    
    # Update based on installation type
    if [[ "$UPDATE_DOCKER" == "true" ]]; then
        update_from_docker
    else
        case $INSTALL_TYPE in
            pip)
                update_from_pip
                ;;
            source)
                update_from_source
                ;;
            *)
                print_warning "Unknown installation type: $INSTALL_TYPE"
                print_info "Attempting to update from source..."
                update_from_source
                ;;
        esac
    fi
    
    # Verify update
    NEW_VERSION=$(get_current_version)
    
    echo ""
    print_section "Update Verification"
    print_result "Old Version" "$CURRENT_VERSION"
    print_result "New Version" "$NEW_VERSION"
    
    if [[ "$CURRENT_VERSION" != "$NEW_VERSION" ]] || [[ "$FORCE" == "true" ]]; then
        print_success "✅ Update successful!"
    else
        print_warning "Version unchanged (up-to-date or forced)"
    fi
    
    # Show quick start
    echo ""
    print_section "Quick Start"
    echo -e "${GREEN}🎉 GitClonePro has been updated!${NC}"
    echo ""
    echo "  gitclone https://github.com/octocat/Hello-World"
    echo "  gitclone --help"
    echo ""
    echo -e "${GREEN}Happy cloning! 🚀${NC}"
}

# ==================== RUN MAIN ====================
main "$@"