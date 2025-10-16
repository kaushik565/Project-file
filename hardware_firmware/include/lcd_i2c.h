#ifndef LCD_I2C_H
#define LCD_I2C_H

void lcd_init(void);
void lcd_clear(void);
void lcd_set_cursor(unsigned char col, unsigned char row);
void lcd_print(const char* str);
void lcd_print_lines(const char* line1, const char* line2);

#endif
