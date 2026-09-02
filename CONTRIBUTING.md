# Contributing to GitClonePro

We welcome contributions! Here's how you can help:

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/GitClonePro
cd GitClonePro

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .
pip install pytest pytest-cov black flake8 mypy

# Run tests
pytest tests/

# Check code style
black gitclone/
flake8 gitclone/