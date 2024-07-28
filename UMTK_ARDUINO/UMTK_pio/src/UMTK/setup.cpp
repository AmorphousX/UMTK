#include "setup.h"


void setPins()
{
  pinMode(SLIDE_CLOCK, INPUT);
  pinMode(SLIDE_DATA, INPUT);
  pinMode(SLIDE_CLOCK_DIR, OUTPUT);
  digitalWrite(SLIDE_CLOCK_DIR, LOW);
  pinMode(SLIDE_DATA_DIR, OUTPUT);
  digitalWrite(SLIDE_DATA_DIR, LOW);

  pinMode(LOADCELL_CLOCK, OUTPUT);
  pinMode(LOADCELL_DATA, INPUT);
  pinMode(LOADCELL_RATE, OUTPUT);

  pinMode(MOTOR_DISABLE, OUTPUT);
  pinMode(M_IN1, OUTPUT);
  pinMode(M_IN2, OUTPUT);
  pinMode(MOTOR_nITRIP, INPUT);
  pinMode(MOTOR_OPENLOAD, INPUT);
  pinMode(MOTOR_nFAULT, INPUT);
  pinMode(MOTOR_nSLEEP, INPUT);
  pinMode(MOTOR_MODE, INPUT);

  pinMode(DISP_CS, OUTPUT);
  pinMode(DISP_DIN, OUTPUT);
  pinMode(DISP_CLK, OUTPUT);

  pinMode(VIN_SENSE, INPUT);
  pinMode(VMOT_SENSE, INPUT);

  pinMode(MOTOR_ISENSE_1, INPUT);
  pinMode(MOTOR_ISENSE_2, INPUT);

  pinMode(SWITCH_JOGUP, INPUT);
  pinMode(SWITCH_JOGDOWN, INPUT);
  pinMode(SWITCH_TARE, INPUT);
  pinMode(SWITCH_START, INPUT);
  pinMode(SWITCH_AUX, INPUT);
}