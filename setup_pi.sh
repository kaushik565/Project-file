#!/bin/bash

# Quick setup script for copying project to Raspberry Pi

echo "Copying Batch Scanning JIG project to Raspberry Pi..."

# Set the target directory
TARGET_DIR="/home/qateam/Desktop/Project file"

# Create target directory if it doesn't exist
sudo mkdir -p "$TARGET_DIR"

# Copy all Python files and configuration
echo "Copying project files..."
sudo cp *.py "$TARGET_DIR/"
sudo cp *.ini "$TARGET_DIR/"
sudo cp *.md "$TARGET_DIR/" 2>/dev/null || true
sudo cp -r systemd "$TARGET_DIR/" 2>/dev/null || true

# Copy batch logs and setup logs if they exist
if [ -d "batch_logs" ]; then
    sudo cp -r batch_logs "$TARGET_DIR/"
fi

if [ -d "Batch_Setup_Logs" ]; then
    sudo cp -r Batch_Setup_Logs "$TARGET_DIR/"
fi

# Set proper ownership
sudo chown -R qateam:qateam "$TARGET_DIR"

# Make scripts executable
sudo chmod +x "$TARGET_DIR"/*.sh 2>/dev/null || true

echo "✓ Project files copied to $TARGET_DIR"
echo ""
echo "Now run the auto-start installation:"
echo "  cd $TARGET_DIR"
echo "  sudo ./install_autostart.sh"