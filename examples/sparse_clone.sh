#!/bin/bash
# ============================================================
# GitClonePro - Sparse Clone Example Script
# ============================================================
# This script demonstrates how to clone only specific files 
# or folders from a repository, saving bandwidth and time.
# 
# Usage: ./sparse_clone.sh [REPO_URL] [PATHS...]
# ============================================================

set -e  # Exit on error
set -o pipefail  # Pipe failures count

# ==================== COLOR CODES ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# ==================== FUNCTIONS ====================
print_header() {
    echo -e "\n${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} ${WHITE}GitClonePro - Sparse Clone Tool v2.0.0${NC}                   ${BLUE}║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}\n"
}

print_section() {
    echo -e "\n${CYAN}▶ ${1}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
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

print_result() {
    echo -e "${PURPLE}📊 ${1}${NC}"
}

# ==================== DEFAULT VALUES ====================
DEFAULT_BRANCH="main"
DEFAULT_DEPTH="1"
DEFAULT_DEST=""

# ==================== PARSE COMMAND LINE ARGUMENTS ====================
REPO_URL=""
PATHS=()
BRANCH="$DEFAULT_BRANCH"
DEPTH="$DEFAULT_DEPTH"
DEST_DIR="$DEFAULT_DEST"
TOKEN="${GITHUB_TOKEN:-}"
USE_SSH="false"

# Show help if no arguments
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 REPO_URL PATHS... [OPTIONS]"
    echo ""
    echo "Arguments:"
    echo "  REPO_URL     GitHub repository URL"
    echo "  PATHS...     Files or folders to clone (space-separated)"
    echo ""
    echo "Options:"
    echo "  --branch BRANCH   Branch to clone (default: main)"
    echo "  --depth N         Shallow clone depth (default: 1)"
    echo "  --dest DIR        Destination directory"
    echo "  --token TOKEN     GitHub personal access token"
    echo "  --ssh             Use SSH instead of HTTPS"
    echo "  --help, -h        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 https://github.com/facebook/react src/ README.md"
    echo "  $0 https://github.com/kubernetes/kubernetes cmd/ --branch master"
    echo "  $0 https://github.com/microsoft/vscode docs/ --depth 5"
    echo ""
    echo "Common sparse paths:"
    echo "  📁 Clone only source code: src/ lib/"
    echo "  📄 Clone only documentation: docs/ README.md"
    echo "  📁 Clone only tests: tests/ __tests__/"
    echo "  📄 Clone only config: .github/ setup.py requirements.txt"
    exit 0
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --depth)
            DEPTH="$2"
            shift 2
            ;;
        --dest)
            DEST_DIR="$2"
            shift 2
            ;;
        --token)
            TOKEN="$2"
            shift 2
            ;;
        --ssh)
            USE_SSH="true"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 REPO_URL PATHS... [OPTIONS]"
            exit 0
            ;;
        -*)
            print_error "Unknown option: $1"
            exit 1
            ;;
        *)
            if [[ -z "$REPO_URL" ]]; then
                REPO_URL="$1"
            else
                PATHS+=("$1")
            fi
            shift
            ;;
    esac
done

# ==================== VALIDATION ====================
print_header

# Check if gitclone is installed
if ! command -v gitclone &> /dev/null; then
    print_error "GitClonePro not found. Please install with: pip install -e ."
    exit 1
fi

# Check if Git is installed
if ! command -v git &> /dev/null; then
    print_error "Git not found. Please install Git first."
    exit 1
fi

# Validate repository URL
if [[ -z "$REPO_URL" ]]; then
    print_error "No repository URL provided."
    echo "Usage: $0 REPO_URL PATHS... [OPTIONS]"
    exit 1
fi

# Validate paths
if [[ ${#PATHS[@]} -eq 0 ]]; then
    print_error "No paths specified. Please provide at least one file or folder to clone."
    echo "Example: $0 https://github.com/user/repo src/ README.md"
    exit 1
fi

# Validate depth
if [[ -n "$DEPTH" ]] && ! [[ "$DEPTH" =~ ^[0-9]+$ ]]; then
    print_warning "Invalid depth: $DEPTH. Using default: 1"
    DEPTH="1"
fi

# Validate branch
if [[ -z "$BRANCH" ]]; then
    BRANCH="main"
fi

# Set destination
if [[ -z "$DEST_DIR" ]]; then
    # Extract repo name from URL
    REPO_NAME=$(basename "$REPO_URL" .git)
    DEST_DIR="./sparse_${REPO_NAME}_$(date +%Y%m%d_%H%M%S)"
fi

# ==================== SHOW CONFIGURATION ====================
print_section "Configuration"
echo -e "  ${WHITE}Repository:${NC} $REPO_URL"
echo -e "  ${WHITE}Branch:${NC}     $BRANCH"
echo -e "  ${WHITE}Depth:${NC}      $DEPTH"
echo -e "  ${WHITE}Paths:${NC}      ${PATHS[*]}"
echo -e "  ${WHITE}Destination:${NC} $DEST_DIR"
[[ -n "$TOKEN" ]] && echo -e "  ${WHITE}Token:${NC}      ${TOKEN:0:8}... (provided)"
[[ "$USE_SSH" == "true" ]] && echo -e "  ${WHITE}SSH:${NC}        Yes"

# Show estimated savings
print_section "Estimated Savings"
echo -e "${CYAN}💡 Sparse clone will download only:${NC}"
for path in "${PATHS[@]}"; do
    echo "  📁 $path"
done
echo -e "${CYAN}This saves bandwidth and time compared to cloning the full repository.${NC}"

# ==================== CONFIRMATION ====================
echo ""
read -p "Proceed with sparse clone? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Operation cancelled."
    exit 0
fi

# ==================== BUILD COMMAND ====================
print_section "Building Command"

CMD="gitclone \"$REPO_URL\" --sparse"

for path in "${PATHS[@]}"; do
    CMD="$CMD \"$path\""
done

CMD="$CMD --branch \"$BRANCH\" --depth $DEPTH --dest \"$DEST_DIR\""

if [[ "$USE_SSH" == "true" ]]; then
    CMD="$CMD --ssh"
fi

if [[ -n "$TOKEN" ]]; then
    CMD="$CMD --token \"$TOKEN\""
fi

echo -e "  ${WHITE}Command:${NC} $CMD"

# ==================== START CLONING ====================
print_section "Starting Sparse Clone"
echo -e "${BLUE}⏳ Cloning only specified paths...${NC}"
echo -e "${BLUE}📁 Destination: $DEST_DIR${NC}\n"

# Record start time
START_TIME=$(date +%s)

# Execute the command
if eval $CMD; then
    # Record end time
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    # ==================== SUMMARY ====================
    print_section "Summary"
    print_success "Sparse clone completed successfully!"
    print_result "Duration: ${DURATION} seconds"
    print_result "Location: $DEST_DIR"
    
    # Check what was cloned
    if [[ -d "$DEST_DIR" ]]; then
        print_section "Cloned Files & Folders"
        
        # Show directory structure
        echo -e "${WHITE}Directory structure:${NC}"
        
        # Check if we can list files
        if command -v tree &> /dev/null; then
            # Use tree if available
            tree -L 3 "$DEST_DIR" || ls -la "$DEST_DIR"
        else
            # Fallback to ls
            ls -la "$DEST_DIR"
            echo ""
            # Recursive list for deeper structure
            find "$DEST_DIR" -type f -o -type d | head -20
        fi
        
        # Show file count
        FILE_COUNT=$(find "$DEST_DIR" -type f 2>/dev/null | wc -l)
        print_result "Files downloaded: $FILE_COUNT"
        
        # Show disk usage
        DISK_USAGE=$(du -sh "$DEST_DIR" 2>/dev/null | cut -f1)
        print_result "Total size: $DISK_USAGE"
        
        # Compare to full clone estimate
        print_info "💡 The full repository would typically be much larger."
        print_info "   Sparse clone saved you bandwidth and storage space."
    fi
    
    # ==================== NEXT STEPS ====================
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✨ Next Steps:${NC}"
    echo "  cd $DEST_DIR"
    echo "  ls -la"
    echo ""
    echo -e "${CYAN}To add more files later:${NC}"
    echo "  git sparse-checkout add <more-paths>"
    echo "  git checkout"
    echo ""
    echo -e "${CYAN}To update to latest version:${NC}"
    echo "  git pull"
    echo ""
    echo -e "${GREEN}Happy sparse coding! 🚀${NC}"
    
else
    # ==================== ERROR HANDLING ====================
    print_error "Sparse clone failed!"
    print_info "Check the error messages above for details."
    
    # Common issues
    echo ""
    echo -e "${YELLOW}Common issues:${NC}"
    echo "  1. Path doesn't exist → Check spelling and case sensitivity"
    echo "  2. Branch doesn't exist → Verify branch name"
    echo "  3. Rate limit exceeded → Provide GitHub token with --token"
    echo "  4. Git version too old → Upgrade Git to 2.25+"
    echo "  5. Repository is private → Use --token or --ssh"
    
    # Check Git version
    GIT_VERSION=$(git --version | awk '{print $3}')
    echo ""
    print_info "Your Git version: $GIT_VERSION (requires 2.25+)"
    
    exit 1
fi

# ==================== CLEANUP ====================
# (Optional) Remove empty directories
find "$DEST_DIR" -type d -empty -delete 2>/dev/null || true

echo -e "\n${GREEN}✅ Done!${NC}"