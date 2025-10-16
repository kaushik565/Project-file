#!/bin/bash

# Create deployment package for Raspberry Pi
# Run this to create a ready-to-deploy package

PACKAGE_NAME="batch-jig-deployment-$(date +%Y%m%d_%H%M%S)"
CURRENT_DIR=$(pwd)

echo "📦 CREATING DEPLOYMENT PACKAGE"
echo "=============================="
echo "Package name: $PACKAGE_NAME"
echo "Source: $CURRENT_DIR"

# Create package directory
mkdir -p "../$PACKAGE_NAME"

# Copy essential files
echo ""
echo "Copying files..."

# Python modules
cp *.py "../$PACKAGE_NAME/"
echo "✅ Python files copied"

# Configuration files
cp *.ini "../$PACKAGE_NAME/"
echo "✅ Configuration files copied"

# Shell scripts  
cp *.sh "../$PACKAGE_NAME/"
echo "✅ Shell scripts copied"

# Documentation
cp *.md "../$PACKAGE_NAME/"
echo "✅ Documentation copied"

# System files
if [ -d "systemd" ]; then
    cp -r systemd "../$PACKAGE_NAME/"
    echo "✅ Systemd files copied"
fi

# Create logs directories
mkdir -p "../$PACKAGE_NAME/batch_logs"
mkdir -p "../$PACKAGE_NAME/Batch_Setup_Logs"
echo "✅ Log directories created"

# Copy sample log files if they exist
if [ -d "batch_logs" ]; then
    cp batch_logs/*.csv "../$PACKAGE_NAME/batch_logs/" 2>/dev/null || true
fi

if [ -d "Batch_Setup_Logs" ]; then
    cp Batch_Setup_Logs/*.csv "../$PACKAGE_NAME/Batch_Setup_Logs/" 2>/dev/null || true
fi

# Create deployment instructions
cat > "../$PACKAGE_NAME/DEPLOY_ON_PI.md" << 'EOF'
# 🚀 Deployment Instructions for Raspberry Pi

## Quick Deployment Steps:

### 1. Copy to Raspberry Pi
```bash
# Copy this entire folder to:
/home/qateam/Desktop/Project file/
```

### 2. Make scripts executable
```bash
cd "/home/qateam/Desktop/Project file"
chmod +x *.sh
```

### 3. Test in development mode
```bash
./switch_mode.sh dev
python3 main.py
```

### 4. Test hardware connections
```bash
# Follow hardware tests in TESTING_DEPLOYMENT_GUIDE.md
```

### 5. Switch to production mode
```bash
./switch_mode.sh prod
python3 main.py
```

### 6. Install auto-start (after testing)
```bash
sudo ./install_autostart_simple.sh
```

### 7. Reboot and verify
```bash
sudo reboot
```

## Files in this package:
- All Python modules for the application
- Configuration files (dev and production)
- Installation and setup scripts  
- Complete documentation
- Systemd service files
- Sample log directories

## Support:
Refer to TESTING_DEPLOYMENT_GUIDE.md for detailed testing procedures.
EOF

# Create version info
cat > "../$PACKAGE_NAME/VERSION_INFO.txt" << EOF
Batch Scanning Jig - Deployment Package
Generated: $(date)
Source: $CURRENT_DIR
Package: $PACKAGE_NAME

Features included:
- QR code validation and batch tracking
- ACTJ mechanical jig integration  
- GPIO LED and buzzer control
- I2C LCD display support
- Auto-start capability
- Production/development mode switching
- Complete logging and monitoring

Hardware requirements:
- Raspberry Pi 3B+ or newer
- ACTJ controller PCB v3.1
- I2C LCD (16x2) at address 0x27
- LEDs on GPIO 20 (red), GPIO 21 (green)
- Buzzer on GPIO 23
- UART connection to ACTJ controller

Installation:
1. Copy to /home/qateam/Desktop/Project file/
2. Follow DEPLOY_ON_PI.md instructions
3. Test thoroughly before production use
EOF

# Make scripts executable in package
chmod +x "../$PACKAGE_NAME"/*.sh

# Create tarball for easy transfer
cd ..
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

echo ""
echo "✅ DEPLOYMENT PACKAGE CREATED"
echo "=============================="
echo "Package directory: ../$PACKAGE_NAME"
echo "Archive file: ../$PACKAGE_NAME.tar.gz"
echo ""
echo "Transfer options:"
echo "1. Copy folder via USB drive"
echo "2. Transfer via SCP: scp -r $PACKAGE_NAME.tar.gz qateam@PI_IP:~/"
echo "3. Use network share"
echo ""
echo "On Raspberry Pi:"
echo "  tar -xzf $PACKAGE_NAME.tar.gz"
echo "  mv $PACKAGE_NAME 'Project file'"
echo "  cd 'Project file'"
echo "  ./test_before_deploy.sh"