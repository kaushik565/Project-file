#include "i2c_lcd.h"

void lcd_init(void) {
    I2C_Init1();
    LCD_Begin(0x27); // Default I2C address, update if needed
}

void lcd_clear(void) {
    LCD_Cmd(LCD_CLEAR);
}

void lcd_set_cursor(unsigned char col, unsigned char row) {
    LCD_Goto(col + 1, row + 1); // 1-based indexing in legacy code
}

void lcd_print(const char* str) {
    LCD_Print_space(str);
}

void lcd_print_lines(const char* line1, const char* line2) {
    LCD_Cmd(LCD_FIRST_ROW);
    LCD_Print_space(line1);
    LCD_Cmd(LCD_SECOND_ROW);
    LCD_Print_space(line2);
}
