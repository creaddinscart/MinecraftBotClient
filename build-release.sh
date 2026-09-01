#!/bin/bash
# MinecraftBotClient Build Script for Release

echo "========================================="
echo "MinecraftBotClient Build Script v1.0.0"
echo "========================================="
echo ""

# Check Python
echo "[1/5] Checking Python installation..."
if ! command -v python &> /dev/null; then
    echo "ERROR: Python not found. Please install Python 3.7+"
    exit 1
fi
echo "✓ Python found: $(python --version)"
echo ""

# Install dependencies
echo "[2/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"
echo ""

# Clean previous builds
echo "[3/5] Cleaning previous builds..."
rm -rf build dist *.spec
echo "✓ Clean complete"
echo ""

# Build executable
echo "[4/5] Building executable with PyInstaller..."
python -m PyInstaller --onefile --windowed --name MinecraftBotClient main.py
if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi
echo "✓ Build complete"
echo ""

# Verify output
echo "[5/5] Verifying build output..."
if [ -f "dist/MinecraftBotClient.exe" ]; then
    SIZE=$(du -h dist/MinecraftBotClient.exe | cut -f1)
    echo "✓ SUCCESS! MinecraftBotClient.exe ($SIZE) created"
    echo ""
    echo "========================================="
    echo "Build completed successfully!"
    echo "Location: dist/MinecraftBotClient.exe"
    echo "========================================="
else
    echo "ERROR: EXE file not found"
    exit 1
fi
