# Makefile for PIC18F4550 Firmware (C18 Compiler)
# Adjust paths and settings for your MPLAB C18 installation

# Compiler and tools
CC = mcc18
LD = mplink
AS = mpasmwin

# Device configuration  
DEVICE = 18F4550

# Directories
SRC_DIR = src
INC_DIR = include
OBJ_DIR = obj
BIN_DIR = bin

# Compiler flags
CFLAGS = -p=$(DEVICE) -I$(INC_DIR) -ml --extended -O

# Linker flags (adjust linker script as needed)
LDFLAGS = /l"$(MCC18_PATH)\lib" "$(MCC18_PATH)\lkr\rm$(DEVICE).lkr" /o$(BIN_DIR)\main.cof

# Source files
SOURCES = $(SRC_DIR)/main.c \
          $(SRC_DIR)/uart.c \
          $(SRC_DIR)/lcd_i2c.c

# Object files
OBJECTS = $(SOURCES:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

# Header dependencies
HEADERS = $(INC_DIR)/pins.h \
          $(INC_DIR)/protocol.h \
          $(INC_DIR)/config_bits.h \
          $(INC_DIR)/uart.h \
          $(INC_DIR)/lcd_i2c.h \
          $(INC_DIR)/delay.h

# Default target
all: directories $(BIN_DIR)/main.hex

# Create directories
directories:
	@if not exist $(OBJ_DIR) mkdir $(OBJ_DIR)
	@if not exist $(BIN_DIR) mkdir $(BIN_DIR)

# Compile C files to object files
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c $(HEADERS)
	$(CC) $(CFLAGS) -fo=$@ $<

# Link object files to create .cof
$(BIN_DIR)/main.cof: $(OBJECTS)
	$(LD) $(LDFLAGS) $(OBJECTS)

# Convert .cof to .hex
$(BIN_DIR)/main.hex: $(BIN_DIR)/main.cof
	mp2hex $(BIN_DIR)\main.cof

# Clean build files
clean:
	@if exist $(OBJ_DIR) rmdir /s /q $(OBJ_DIR)
	@if exist $(BIN_DIR) rmdir /s /q $(BIN_DIR)

# Programming target (adjust programmer and device as needed)
program: $(BIN_DIR)/main.hex
	@echo Programming $(DEVICE) with $(BIN_DIR)/main.hex
	@echo Use your preferred programmer (MPLAB IPE, PICkit, etc.)
	@echo Example: pk2cmd -PPIC$(DEVICE) -M -F$(BIN_DIR)/main.hex

# Help
help:
	@echo Available targets:
	@echo   all      - Build firmware (default)
	@echo   clean    - Remove build files
	@echo   program  - Program device (manual step)
	@echo   help     - Show this help

.PHONY: all clean program help directories

# Alternative MPLAB X project configuration:
# If using MPLAB X IDE instead of command line:
# 1. Create new project for PIC18F4550
# 2. Add all .c and .h files to project
# 3. Configure compiler settings:
#    - Optimization: -O (default)
#    - Include paths: include/
# 4. Build project to generate .hex file