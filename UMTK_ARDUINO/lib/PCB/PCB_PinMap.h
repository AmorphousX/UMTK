// Pin mapping for UMTK PCB V1.5
#pragma once

#define SLIDE_CLOCK 3
#define SLIDE_DATA 4
#define SLIDE_CLOCK_DIR 23 // Low, Input only
#define SLIDE_DATA_DIR 24 // Low,Input only

#define LOADCELL_CLOCK 5
#define LOADCELL_DATA 6
#define LOADCELL_RATE 25

#define MOTOR_DISABLE 7
#define M_IN1 8
#define M_IN2 9
#define MOTOR_nITRIP 10
#define MOTOR_OPENLOAD 11
#define MOTOR_nFAULT 12

// GREEN V1.5 HAS nSLEEP on 13
// BACK V1.5 HAS nSLEEP on 14, 13 is used as indicator
// #define MOTOR_nSLEEP 13
#define MOTOR_nSLEEP 14
#define LED_BLINKABLE 1
#define MOTOR_MODE 22

#define DISP_CS 26
#define DISP_DIN 51 // Refenece Only, This will be used by SPI
#define DISP_CLK 52 // Refenece Only, This will be used by SPI

#define VIN_SENSE A0
#define VMOT_SENSE A1
#define MOTOR_ISENSE_1 A2
#define MOTOR_ISENSE_2 A3

#define SWITCH_JOGUP A8 // SW1
#define SWITCH_JOGDOWN A9 // SW2
#define SWITCH_TARE A10 // SW3
#define SWITCH_START A11 // SW4
#define SWITCH_AUX A12 // SW5

#define VSENSE_iK 18.6181818182
#define VMOT_ISENSE_iK  126.603636364

#define STALL_AMPS_THREASHOLD 5.0

//Change this calibration factor as per your load cell 
// once it is found you many need to vary it in thousands
#define FACTORY_CALIBRATION_DEFAULT 2203 //-106600 worked for my 40Kg max scale setup 