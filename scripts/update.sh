#!/bin/bash
# Update GitClonePro to latest version

set -e

echo "🔄 Updating GitClonePro..."

# Check if installed via pip
if pip3 show gitclonepro &> /dev/null; then
    echo "📦 Updating via pip..."
    pip3 install --upgrade gitclonepro
    echo "✅ Update complete!"
    exit 0
fi

# Check if installed from source
if [ -d "$HOME/.local/lib/python3*/site-packages/gitclone" ] || [ -d "$(pwd)/gitclone" ]; then
    echo "📦 Updating from source..."
    
    # Find gitclone directory
    if [ -d "$(pwd)/gitclone" ]; then
        GITCLONE_DIR="$(pwd)"
    else
        GITCLONE_DIR="$HOME/.local/src/gitclonepro"
    fi
    
    cd "$GITCLONE_DIR"
    git pull origin main
    pip3 install -e .
    
    echo "✅ Update complete!"
    exit 0
fi

echo "❌ GitClonePro not found. Please install first:"
echo "  pip3 install gitclonepro"
echo "  or"
echo "  git clone https://github.com/yourusername/GitClonePro"
echo "  cd GitClonePro && pip3 install -e ."