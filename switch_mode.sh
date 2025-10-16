#!/bin/bash

# Switch between development and production settings

CURRENT_SETTINGS="settings.ini"
DEV_SETTINGS="settings.ini.sample"  
PROD_SETTINGS="settings_production.ini"

case "$1" in
    "dev"|"development")
        echo "Switching to development settings..."
        cp "$DEV_SETTINGS" "$CURRENT_SETTINGS"
        echo "✓ Development mode enabled (mock hardware, mock LCD)"
        ;;
    "prod"|"production"|"pi")
        echo "Switching to production settings..."
        cp "$PROD_SETTINGS" "$CURRENT_SETTINGS"
        echo "✓ Production mode enabled (real GPIO, real LCD)"
        ;;
    "status")
        echo "Current settings mode:"
        if grep -q "controller = mock" "$CURRENT_SETTINGS" 2>/dev/null; then
            echo "  Hardware: Development (mock)"
        elif grep -q "controller = gpio" "$CURRENT_SETTINGS" 2>/dev/null; then
            echo "  Hardware: Production (GPIO)"
        else
            echo "  Hardware: Unknown"
        fi
        
        if grep -q "type = mock" "$CURRENT_SETTINGS" 2>/dev/null; then
            echo "  LCD: Development (mock)"
        elif grep -q "type = i2c" "$CURRENT_SETTINGS" 2>/dev/null; then
            echo "  LCD: Production (I2C)"
        else
            echo "  LCD: Unknown"
        fi
        ;;
    *)
        echo "Usage: $0 {dev|prod|status}"
        echo ""
        echo "  dev     - Switch to development settings (mock hardware)"
        echo "  prod    - Switch to production settings (real GPIO/LCD)"  
        echo "  status  - Show current configuration mode"
        echo ""
        echo "Examples:"
        echo "  $0 dev      # For development/testing"
        echo "  $0 prod     # For Raspberry Pi deployment"
        echo "  $0 status   # Check current mode"
        exit 1
        ;;
esac