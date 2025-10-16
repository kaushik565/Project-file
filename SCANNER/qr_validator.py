#!/usr/bin/env python3
"""
QR Code Validation Module for Matrix Scanner
Provides comprehensive validation for QR codes in manufacturing process
"""

import re
import json
from datetime import datetime
from typing import Tuple, Dict, Any

class QRValidator:
    def __init__(self, config_file="/SCANNER/validation_config.json"):
        """Initialize QR validator with configuration"""
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load validation configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Default configuration if file doesn't exist
            self.config = {
                "matrix_validation": {
                    "min_length": 8,
                    "max_length": 20,
                    "allowed_prefixes": ["M", "MX", "MAT"],
                    "pattern": "^(M|MX|MAT)[A-Z0-9]+$",
                    "required_sections": 2
                },
                "cartridge_validation": {
                    "min_length": 10,
                    "max_length": 25,
                    "allowed_prefixes": ["C", "CAR", "CART"],
                    "pattern": "^[A-Z0-9]{10,25}$",
                    "checksum_enabled": False,
                    "date_validation": True,
                    "lot_validation": True
                },
                "general_validation": {
                    "allowed_chars": "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
                    "forbidden_sequences": ["00000", "11111", "AAAAA"],
                    "min_unique_chars": 3
                }
            }
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def validate_qr_code(self, qr_code: str, qr_type: str = "auto") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Main validation function for QR codes
        
        Args:
            qr_code: The QR code string to validate
            qr_type: Type of QR code ('matrix', 'cartridge', or 'auto')
            
        Returns:
            Tuple of (is_valid, error_message, validation_details)
        """
        if not qr_code or not isinstance(qr_code, str):
            return False, "QR code is empty or invalid type", {}
        
        qr_code = qr_code.strip().upper()
        
        # Auto-detect QR type if not specified
        if qr_type == "auto":
            qr_type = self.detect_qr_type(qr_code)
        
        # Basic validation first
        basic_valid, basic_error = self.basic_validation(qr_code)
        if not basic_valid:
            return False, basic_error, {"qr_type": qr_type}
        
        # Type-specific validation
        if qr_type == "matrix":
            return self.validate_matrix_qr(qr_code)
        elif qr_type == "cartridge":
            return self.validate_cartridge_qr(qr_code)
        else:
            return False, f"Unknown QR type: {qr_type}", {"qr_type": qr_type}
    
    def detect_qr_type(self, qr_code: str) -> str:
        """Auto-detect QR code type based on patterns"""
        matrix_prefixes = self.config["matrix_validation"]["allowed_prefixes"]
        cartridge_prefixes = self.config["cartridge_validation"]["allowed_prefixes"]
        
        for prefix in matrix_prefixes:
            if qr_code.startswith(prefix):
                return "matrix"
        
        for prefix in cartridge_prefixes:
            if qr_code.startswith(prefix):
                return "cartridge"
        
        # Default classification based on length
        if len(qr_code) < 10:
            return "matrix"
        else:
            return "cartridge"
    
    def basic_validation(self, qr_code: str) -> Tuple[bool, str]:
        """Perform basic validation checks"""
        general_config = self.config["general_validation"]
        
        # Check for forbidden characters
        allowed_chars = set(general_config["allowed_chars"])
        for char in qr_code:
            if char not in allowed_chars:
                return False, f"Invalid character '{char}' in QR code"
        
        # Check for forbidden sequences
        for seq in general_config["forbidden_sequences"]:
            if seq in qr_code:
                return False, f"Forbidden sequence '{seq}' found in QR code"
        
        # Check minimum unique characters
        unique_chars = len(set(qr_code))
        min_unique = general_config["min_unique_chars"]
        if unique_chars < min_unique:
            return False, f"QR code must have at least {min_unique} unique characters"
        
        return True, ""
    
    def validate_matrix_qr(self, qr_code: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate matrix QR codes"""
        config = self.config["matrix_validation"]
        details = {"qr_type": "matrix", "original_code": qr_code}
        
        # Length validation
        if len(qr_code) < config["min_length"]:
            return False, f"Matrix QR too short (min {config['min_length']} chars)", details
        
        if len(qr_code) > config["max_length"]:
            return False, f"Matrix QR too long (max {config['max_length']} chars)", details
        
        # Prefix validation
        valid_prefix = False
        for prefix in config["allowed_prefixes"]:
            if qr_code.startswith(prefix):
                valid_prefix = True
                details["prefix"] = prefix
                details["matrix_id"] = qr_code[len(prefix):]
                break
        
        if not valid_prefix:
            return False, f"Invalid matrix prefix. Allowed: {config['allowed_prefixes']}", details
        
        # Pattern validation
        if not re.match(config["pattern"], qr_code):
            return False, "Matrix QR doesn't match required pattern", details
        
        # Additional matrix-specific validations
        matrix_id = details["matrix_id"]
        if len(matrix_id) < 3:
            return False, "Matrix ID too short", details
        
        details["validation_passed"] = True
        details["timestamp"] = datetime.now().isoformat()
        
        return True, "Matrix QR validation passed", details
    
    def validate_cartridge_qr(self, qr_code: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate cartridge QR codes"""
        config = self.config["cartridge_validation"]
        details = {"qr_type": "cartridge", "original_code": qr_code}
        
        # Length validation
        if len(qr_code) < config["min_length"]:
            return False, f"Cartridge QR too short (min {config['min_length']} chars)", details
        
        if len(qr_code) > config["max_length"]:
            return False, f"Cartridge QR too long (max {config['max_length']} chars)", details
        
        # Pattern validation
        if not re.match(config["pattern"], qr_code):
            return False, "Cartridge QR doesn't match required pattern", details
        
        # Checksum validation (if enabled)
        if config.get("checksum_enabled", False):
            checksum_valid, checksum_error = self.validate_checksum(qr_code)
            if not checksum_valid:
                return False, f"Checksum validation failed: {checksum_error}", details
        
        # Date validation (if QR contains date info)
        if config.get("date_validation", False):
            date_valid, date_error = self.validate_date_in_qr(qr_code)
            if not date_valid:
                return False, f"Date validation failed: {date_error}", details
        
        # Lot validation
        if config.get("lot_validation", False):
            lot_valid, lot_error = self.validate_lot_info(qr_code)
            if not lot_valid:
                return False, f"Lot validation failed: {lot_error}", details
        
        details["validation_passed"] = True
        details["timestamp"] = datetime.now().isoformat()
        
        return True, "Cartridge QR validation passed", details
    
    def validate_checksum(self, qr_code: str) -> Tuple[bool, str]:
        """Validate checksum in QR code (implement your checksum algorithm)"""
        # Example: Simple modulo 10 checksum for last digit
        if len(qr_code) < 2:
            return False, "QR too short for checksum"
        
        try:
            data_part = qr_code[:-1]
            checksum_digit = int(qr_code[-1])
            
            # Calculate checksum (example algorithm)
            calculated_sum = sum(int(c) if c.isdigit() else ord(c) % 10 for c in data_part)
            expected_checksum = calculated_sum % 10
            
            if checksum_digit == expected_checksum:
                return True, ""
            else:
                return False, f"Expected checksum {expected_checksum}, got {checksum_digit}"
        
        except (ValueError, IndexError) as e:
            return False, f"Checksum calculation error: {str(e)}"
    
    def validate_date_in_qr(self, qr_code: str) -> Tuple[bool, str]:
        """Validate date information in QR code"""
        # Example: Look for YYMMDD pattern in QR code
        date_patterns = [
            r'(\d{6})',  # YYMMDD
            r'(\d{8})',  # YYYYMMDD
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, qr_code)
            for match in matches:
                try:
                    if len(match) == 6:  # YYMMDD
                        year = 2000 + int(match[:2])
                        month = int(match[2:4])
                        day = int(match[4:6])
                    elif len(match) == 8:  # YYYYMMDD
                        year = int(match[:4])
                        month = int(match[4:6])
                        day = int(match[6:8])
                    else:
                        continue
                    
                    # Validate date
                    test_date = datetime(year, month, day)
                    
                    # Check if date is reasonable (not too old or future)
                    current_date = datetime.now()
                    if test_date > current_date:
                        return False, "Date is in the future"
                    
                    # Check if date is not too old (e.g., max 5 years)
                    age_days = (current_date - test_date).days
                    if age_days > 1825:  # 5 years
                        return False, "Date is too old"
                    
                    return True, ""
                
                except ValueError:
                    continue
        
        return True, ""  # No date pattern found, assume valid
    
    def validate_lot_info(self, qr_code: str) -> Tuple[bool, str]:
        """Validate lot information in QR code"""
        # Example: Check for lot patterns
        lot_patterns = [
            r'LOT([A-Z0-9]{3,8})',
            r'L([A-Z0-9]{3,8})',
            r'([A-Z]{2,3}\d{3,6})'
        ]
        
        for pattern in lot_patterns:
            matches = re.findall(pattern, qr_code)
            if matches:
                lot_id = matches[0]
                # Add specific lot validation logic here
                if len(lot_id) < 3:
                    return False, "Lot ID too short"
                return True, ""
        
        return True, ""  # No lot pattern found, assume valid
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics and configuration info"""
        return {
            "config": self.config,
            "validator_version": "1.0",
            "last_updated": datetime.now().isoformat()
        }

# Convenience functions for backward compatibility
def validate_qr_code(qr_code: str, qr_type: str = "auto") -> Tuple[bool, str]:
    """Quick validation function"""
    validator = QRValidator()
    is_valid, error_msg, _ = validator.validate_qr_code(qr_code, qr_type)
    return is_valid, error_msg

def validate_matrix_qr(qr_code: str) -> Tuple[bool, str]:
    """Validate matrix QR code"""
    return validate_qr_code(qr_code, "matrix")

def validate_cartridge_qr(qr_code: str) -> Tuple[bool, str]:
    """Validate cartridge QR code"""
    return validate_qr_code(qr_code, "cartridge")

# Test function
if __name__ == "__main__":
    validator = QRValidator()
    
    # Test cases
    test_codes = [
        ("M12345678", "matrix"),
        ("CART1234567890", "cartridge"),
        ("INVALID@CODE", "auto"),
        ("MX240125001", "matrix")
    ]
    
    for code, qr_type in test_codes:
        is_valid, error, details = validator.validate_qr_code(code, qr_type)
        print(f"QR: {code} | Type: {qr_type} | Valid: {is_valid} | Error: {error}")