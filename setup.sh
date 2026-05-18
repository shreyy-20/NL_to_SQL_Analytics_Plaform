#!/bin/bash

echo "🚀 Setting up KrishiQuery..."

# Install Python deps
pip install -r requirements.txt

# Setup DB
python scripts/setup_database.py
python scripts/seed_data.py

echo "✅ Setup complete"