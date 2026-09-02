#!/bin/bash
# ============================================================
# Batch Clone with Advanced Filtering
# ============================================================
# This script shows how to clone repositories with various
# filters and options for different use cases.
# ============================================================

set -e

# ==================== COLOR CODES ====================
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} ${CYAN}Batch Clone with Filters${NC}                                       ${BLUE}║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}\n"
}

# ==================== EXAMPLE FUNCTIONS ====================
example_public_org() {
    echo -e "\n${GREEN}📦 Example 1: Clone all public repos from an organization${NC}"
    echo "----------------------------------------"
    echo "Clones all public repositories from Kubernetes"
    echo ""
    gitclone --owner kubernetes \
        --type public \
        --threads 8 \
        --depth 1 \
        --dest ./clones/kubernetes-all
}

example_private_repos() {
    echo -e "\n${GREEN}📦 Example 2: Clone private repositories (requires token)${NC}"
    echo "----------------------------------------"
    echo "Clones all private repos from your account"
    echo "⚠️  Requires GITHUB_TOKEN environment variable"
    echo ""
    if [[ -n "$GITHUB_TOKEN" ]]; then
        gitclone --owner your-username \
            --type private \
            --threads 4 \
            --dest ./clones/private-repos
    else
        echo -e "${YELLOW}⚠️  GITHUB_TOKEN not set. Skipping...${NC}"
    fi
}

example_with_exclusions() {
    echo -e "\n${GREEN}📦 Example 3: Clone with exclusions${NC}"
    echo "----------------------------------------"
    echo "Clones all repos except specific ones"
    echo ""
    gitclone --owner microsoft \
        --type public \
        --threads 6 \
        --exclude vscode typescript \
        --dest ./clones/microsoft-no-vscode
}

example_mirror_backup() {
    echo -e "\n${GREEN}📦 Example 4: Create mirror backup of all repos${NC}"
    echo "----------------------------------------"
    echo "Creates bare mirror clones for backup"
    echo ""
    gitclone --owner google \
        --type public \
        --mirror \
        --threads 4 \
        --depth 1 \
        --dest ./clones/google-mirror
}

example_ssh_clones() {
    echo -e "\n${GREEN}📦 Example 5: Clone using SSH${NC}"
    echo "----------------------------------------"
    echo "Uses SSH instead of HTTPS for authentication"
    echo "⚠️  Requires SSH keys configured with GitHub"
    echo ""
    gitclone --owner octocat \
        --type public \
        --ssh \
        --threads 2 \
        --dest ./clones/octocat-ssh
}

example_sources_only() {
    echo -e "\n${GREEN}📦 Example 6: Clone only source repositories${NC}"
    echo "----------------------------------------"
    echo "Excludes forks and private repos"
    echo ""
    gitclone --owner facebook \
        --type sources \
        --threads 6 \
        --dest ./clones/facebook-sources
}

example_latest_commits() {
    echo -e "\n${GREEN}📦 Example 7: Clone only latest commit${NC}"
    echo "----------------------------------------"
    echo "Saves bandwidth by only cloning the latest commit"
    echo ""
    gitclone --owner angular \
        --type public \
        --depth 1 \
        --threads 8 \
        --dest ./clones/angular-shallow
}

example_complete_backup() {
    echo -e "\n${GREEN}📦 Example 8: Complete backup with all branches${NC}"
    echo "----------------------------------------"
    echo "Clones full repositories with all branches and tags"
    echo ""
    gitclone --owner apache \
        --type public \
        --threads 4 \
        --dest ./clones/apache-full
}

# ==================== MAIN ====================
print_header

echo "This script demonstrates various batch cloning scenarios."
echo ""
echo "Available examples:"
echo "  1) Clone all public repos (Kubernetes)"
echo "  2) Clone private repos (requires token)"
echo "  3) Clone with exclusions (Microsoft)"
echo "  4) Mirror backup (Google)"
echo "  5) Clone using SSH (Octocat)"
echo "  6) Clone source repos only (Facebook)"
echo "  7) Clone only latest commit (Angular)"
echo "  8) Complete backup with all branches (Apache)"
echo "  a) Run all examples"
echo "  q) Quit"
echo ""
read -p "Select an option: " choice

case $choice in
    1) example_public_org ;;
    2) example_private_repos ;;
    3) example_with_exclusions ;;
    4) example_mirror_backup ;;
    5) example_ssh_clones ;;
    6) example_sources_only ;;
    7) example_latest_commits ;;
    8) example_complete_backup ;;
    a|A)
        echo -e "\n${CYAN}Running all examples...${NC}"
        mkdir -p ./clones
        example_public_org
        example_with_exclusions
        example_mirror_backup
        example_sources_only
        example_latest_commits
        # Skip private and SSH as they need extra setup
        echo -e "\n${GREEN}✅ All examples completed!${NC}"
        ;;
    q|Q)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo -e "\n${GREEN}✅ Example completed! Check the ./clones/ directory.${NC}"