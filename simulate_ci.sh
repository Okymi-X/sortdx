#!/bin/bash
# Script de simulation du workflow CI localement

set -e

echo "🔄 Simulation du workflow CI..."

echo "📦 Installation des dépendances..."
python -m pip install --upgrade pip
pip install -e ".[dev,full]"

echo "🔍 Vérification avec flake8..."
flake8 sortx tests --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 sortx tests --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

echo "🎨 Vérification du formatage avec black..."
black --check sortx tests

echo "📋 Vérification de l'ordre des imports avec isort..."
isort --check-only sortx tests

echo "🔬 Vérification des types avec mypy..."
mypy sortx --ignore-missing-imports || echo "⚠️ Mypy warnings (non-bloquant)"

echo "🧪 Exécution des tests avec pytest..."
pytest --cov=sortx --cov-report=xml --cov-report=term-missing

echo "✅ Toutes les vérifications ont réussi!"
