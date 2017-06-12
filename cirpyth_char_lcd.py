"""
`char_lcd` -character lcd module 
=================================================
module for interfacing with character lcds
""" 

import time 
import math
import busio
import digitalio
from board import *

# Commands
LCD_CLEARDISPLAY        = 0x01
LCD_RETURNHOME          = 0x02
LCD_ENTRYMODESET        = 0x04
LCD_DISPLAYCONTROL      = 0x08
LCD_CURSORSHIFT         = 0x10
LCD_FUNCTIONSET         = 0x20
LCD_SETCGRAMADDR        = 0x40
LCD_SETDDRAMADDR        = 0x80

# Entry flags
LCD_ENTRYRIGHT          = 0x00
LCD_ENTRYLEFT           = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# Control flags
LCD_DISPLAYON           = 0x04
LCD_DISPLAYOFF          = 0x00
LCD_CURSORON            = 0x02
LCD_CURSOROFF           = 0x00
LCD_BLINKON             = 0x01
LCD_BLINKOFF            = 0x00

# Move flags
LCD_DISPLAYMOVE         = 0x08
LCD_CURSORMOVE          = 0x00
LCD_MOVERIGHT           = 0x04
LCD_MOVELEFT            = 0x00

# Function set flags
LCD_8BITMODE            = 0x10
LCD_4BITMODE            = 0x00
LCD_2LINE               = 0x08
LCD_1LINE               = 0x00
LCD_5x10DOTS            = 0x04
LCD_5x8DOTS             = 0x00


# Offset for up to 4 rows.
LCD_ROW_OFFSETS         = (0x00, 0x40, 0x14, 0x54)

class CircuitPython_CharLCD(object):
	""" Character LCD Class"""
	def __init__(self, rs, en, d4, d5, d6, d7, cols, lines):
		#	save config. attributes 
		self.cols = cols
		self.lines = lines 
		self.rs = rs
		self.en = en
		self.d4 = d4
		self.d5 = d5
		self.d6 = d6
		self.d7 = d7
		#	switch all pins to output
		for pin in(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7):
			pin.switch_to_output()
		#	init. display 
		self.write8(0x33)
		self.write8(0x32)
		#  init. display control
		self.displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
		#  init display function
		self.displayfunction = LCD_4BITMODE | LCD_1LINE | LCD_2LINE | LCD_5x8DOTS
		#  init display mode 
		self.displaymode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
		#  write to display control
		self.write8(LCD_DISPLAYCONTROL | displaycontrol)
		#  write displayfunction
		self.write8(LCD_FUNCTIONSET | displayfunction)
		#  set the entry mode
		self.write8(LCD_ENTRYMODESET | displaymode)
		self.clear()

	def home(self):
		"""moves the cursor back to its home"""
		self.write8(LCD_RETURNHOME) # set cursor position to 0
		self.time.sleep(0.003) # 3000microsec. sleep

	def clear(self):
		"""Enable or disable the display.  Set enable to True to enable."""
		self.write8(LCD_CLEARDISPLAY) # clear display
		self.time.sleep(0.003) # 3000microsec. sleep

	def set_cursor(self, col, row):
		"""Move the cursor to an explicit column and row position."""
		#  move cursor to explicit column/row position
		# Clamp row to the last row of the display
		if row > self.lines:
			row = self.lines - 1 
		# Set location
		self.write8(LCD_SETDDRAMADDR | (col + LCD_ROW_OFFSETS[row]))

	def enable_display(self, enable):
		   """Enable or disable the display.  Set enable to True to enable."""
			if enable:
				self.displaycontrol |= LCD_DISPLAYON
			else:
				self.displaycontrol &= ~LCD_DISPLAYON
			self.write8(LCD_DISPLAYCONTROL | self.displaycontrol)

	#  write text to display 
	def message(self, text):
		line = 0
		#  iterate thru each char
		for char in text:
			# if character is \n, go to next line
			if char == '\n':
				line += 1
				#  move to left/right depending on text direction
				col = 0 if self.displaymode & LCD_ENTRYLEFT > 0 else self.cols-1
				self.set_cursor(col, line)
			# Write character to display 
			else:
				self.write8(ord(char), True)


 
	def write8(self, value, char_mode = False):
		"""Write 8b value in char or data mode. 0<=val<=255.
		char_mode = True if char data, False if non-character
		data (default)"""
		#  one millisec delay to prevent writing too quickly.
		self.time.sleep(0.001)
		#  set character/data bit. (charmode = False)
		self.lcd_rs.value = 0
		# WRITE upper 4 bits
		self.d4.value = ((value >> 4) & 1) > 0
		self.d5.value = ((value >> 5) & 1) > 0
		self.d6.value = ((value >> 6) & 1) > 0
		self.d7.value = ((value >> 7) & 1) > 0
		#  send command
		self.pulse_enable()
		# WRITE lower 4 bits 
		self.d4.value = (value        & 1) > 0
		self.d5.value = ((value >> 1) & 1) > 0
		self.d6.value = ((value >> 2) & 1) > 0
		self.d7.value = ((value >> 3) & 1) > 0
		self.pulse_enable()

	def pulse_enable(self):
	""" Pulses clockEN line off->on->off to send command"""
		self.en.value = False 
		# 1microsec pause
		self.time.sleep(0.0000001)
		self.en.value = True
		# 1microsec pause
		self.time.sleep(0.0000001)
		self.en.value = False
		# 1microsec pause
		self.time.sleep(0.0000001)
	



