#!/bin/bash
# ============================================================
# GitClonePro - Batch Clone Example Script
# ============================================================
# This script demonstrates how to clone multiple repositories
# in parallel from GitHub users or organizations.
# 
# Usage: ./batch_clone.sh [owner] [options]
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
    echo -e "${BLUE}║${NC} ${WHITE}GitClonePro - Batch Clone Tool v2.0.0${NC}                     ${BLUE}║${NC}"
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

# ==================== CONFIGURATION ====================
# Default values
DEFAULT_OWNER="octocat"
DEFAULT_THREADS=4
DEFAULT_TYPE="public"
DEFAULT_DEPTH=""
DEFAULT_MIRROR="false"
DEFAULT_SSH="false"
DEFAULT_DEST=""

# Load configuration from environment or use defaults
OWNER="${1:-$DEFAULT_OWNER}"
THREADS="${GITCLONE_THREADS:-$DEFAULT_THREADS}"
REPO_TYPE="${GITCLONE_TYPE:-$DEFAULT_TYPE}"
DEPTH="${GITCLONE_DEPTH:-$DEFAULT_DEPTH}"
MIRROR="${GITCLONE_MIRROR:-$DEFAULT_MIRROR}"
USE_SSH="${GITCLONE_SSH:-$DEFAULT_SSH}"
DEST_DIR="${GITCLONE_DEST:-$DEFAULT_DEST}"

# GitHub token from environment
TOKEN="${GITHUB_TOKEN:-}"

# ==================== PARSE COMMAND LINE ARGUMENTS ====================
while [[ $# -gt 0 ]]; do
    case $1 in
        --threads)
            THREADS="$2"
            shift 2
            ;;
        --type)
            REPO_TYPE="$2"
            shift 2
            ;;
        --depth)
            DEPTH="$2"
            shift 2
            ;;
        --mirror)
            MIRROR="true"
            shift
            ;;
        --ssh)
            USE_SSH="true"
            shift
            ;;
        --dest)
            DEST_DIR="$2"
            shift 2
            ;;
        --token)
            TOKEN="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OWNER] [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --threads N      Number of parallel clones (default: 4)"
            echo "  --type TYPE      Repository type: all, public, private, forks (default: public)"
            echo "  --depth N        Shallow clone depth"
            echo "  --mirror         Clone as mirror (bare repository)"
            echo "  --ssh            Use SSH instead of HTTPS"
            echo "  --dest DIR       Destination directory"
            echo "  --token TOKEN    GitHub personal access token"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  GITHUB_TOKEN      GitHub personal access token"
            echo "  GITCLONE_THREADS  Default thread count"
            echo "  GITCLONE_TYPE     Default repository type"
            echo "  GITCLONE_DEST     Default destination directory"
            echo ""
            echo "Examples:"
            echo "  $0 microsoft --type public --threads 8"
            echo "  $0 google --depth 1 --mirror"
            echo "  $0 kubernetes --ssh --type all"
            exit 0
            ;;
        *)
            if [[ -z "$OWNER" || "$OWNER" == "$DEFAULT_OWNER" ]]; then
                OWNER="$1"
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

# Validate owner
if [[ -z "$OWNER" ]]; then
    print_error "No owner specified. Please provide a GitHub username or organization."
    echo ""
    echo "Usage: $0 [OWNER] [OPTIONS]"
    echo "Example: $0 microsoft --type public"
    exit 1
fi

# Validate thread count
if ! [[ "$THREADS" =~ ^[0-9]+$ ]] || [[ "$THREADS" -lt 1 ]]; then
    print_warning "Invalid thread count: $THREADS. Using default: 4"
    THREADS=4
fi

# Validate type
if [[ ! "$REPO_TYPE" =~ ^(all|public|private|forks|sources)$ ]]; then
    print_warning "Invalid type: $REPO_TYPE. Using default: public"
    REPO_TYPE="public"
fi

# Validate depth
if [[ -n "$DEPTH" ]] && ! [[ "$DEPTH" =~ ^[0-9]+$ ]]; then
    print_warning "Invalid depth: $DEPTH. Ignoring."
    DEPTH=""
fi

# Set destination
if [[ -z "$DEST_DIR" ]]; then
    DEST_DIR="./clones_${OWNER}_$(date +%Y%m%d_%H%M%S)"
fi

# ==================== SHOW CONFIGURATION ====================
print_section "Configuration"
echo -e "  ${WHITE}Owner:${NC}       $OWNER"
echo -e "  ${WHITE}Threads:${NC}      $THREADS"
echo -e "  ${WHITE}Type:${NC}         $REPO_TYPE"
[[ -n "$DEPTH" ]] && echo -e "  ${WHITE}Depth:${NC}       $DEPTH"
[[ "$MIRROR" == "true" ]] && echo -e "  ${WHITE}Mirror:${NC}      Yes"
[[ "$USE_SSH" == "true" ]] && echo -e "  ${WHITE}SSH:${NC}         Yes"
echo -e "  ${WHITE}Destination:${NC} $DEST_DIR"
[[ -n "$TOKEN" ]] && echo -e "  ${WHITE}Token:${NC}       ${TOKEN:0:8}... (provided)"

# ==================== BUILD COMMAND ====================
print_section "Building Command"

CMD="gitclone --owner \"$OWNER\" --type \"$REPO_TYPE\" --threads $THREADS"

if [[ -n "$DEPTH" ]]; then
    CMD="$CMD --depth $DEPTH"
fi

if [[ "$MIRROR" == "true" ]]; then
    CMD="$CMD --mirror"
fi

if [[ "$USE_SSH" == "true" ]]; then
    CMD="$CMD --ssh"
fi

if [[ -n "$DEST_DIR" ]]; then
    CMD="$CMD --dest \"$DEST_DIR\""
fi

if [[ -n "$TOKEN" ]]; then
    CMD="$CMD --token \"$TOKEN\""
fi

echo -e "  ${WHITE}Command:${NC} $CMD"

# ==================== CONFIRMATION ====================
echo ""
read -p "Proceed with cloning? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Operation cancelled."
    exit 0
fi

# ==================== START CLONING ====================
print_section "Starting Batch Clone"
echo -e "${BLUE}⏳ Cloning repositories from $OWNER...${NC}"
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
    print_success "Batch clone completed successfully!"
    print_result "Duration: ${DURATION} seconds"
    print_result "Location: $DEST_DIR"
    
    # Count repositories cloned
    if [[ -d "$DEST_DIR" ]]; then
        REPO_COUNT=$(find "$DEST_DIR" -maxdepth 1 -type d | wc -l)
        REPO_COUNT=$((REPO_COUNT - 1))  # Subtract the directory itself
        print_result "Repositories cloned: $REPO_COUNT"
    fi
    
    # Show disk usage
    if [[ -d "$DEST_DIR" ]]; then
        DISK_USAGE=$(du -sh "$DEST_DIR" 2>/dev/null | cut -f1)
        print_result "Total size: $DISK_USAGE"
    fi
    
    # List repositories
    if [[ -d "$DEST_DIR" ]] && [[ $(ls -1 "$DEST_DIR" | wc -l) -gt 0 ]]; then
        print_section "Cloned Repositories"
        ls -la "$DEST_DIR" | grep -E "^d" | tail -n +2 | awk '{print "  📁 " $9}'
    fi
    
    # ==================== NEXT STEPS ====================
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✨ Next Steps:${NC}"
    echo "  cd $DEST_DIR"
    echo "  ls -la"
    echo ""
    echo -e "${CYAN}To update all repositories later:${NC}"
    echo "  for repo in $DEST_DIR/*; do cd \$repo && git pull && cd -; done"
    echo ""
    echo -e "${GREEN}Happy coding! 🚀${NC}"
    
else
    # ==================== ERROR HANDLING ====================
    print_error "Batch clone failed!"
    print_info "Check the error messages above for details."
    
    # Common issues
    echo ""
    echo -e "${YELLOW}Common issues:${NC}"
    echo "  1. Rate limit exceeded → Provide GitHub token with --token"
    echo "  2. Network issues → Check internet connection"
    echo "  3. Invalid owner → Verify the username/organization exists"
    echo "  4. Permission denied → Use SSH or token authentication"
    
    exit 1
fi

# ==================== CLEANUP ====================
# (Optional) Remove empty directories
find "$DEST_DIR" -type d -empty -delete 2>/dev/null || true

echo -e "\n${GREEN}✅ Done!${NC}"