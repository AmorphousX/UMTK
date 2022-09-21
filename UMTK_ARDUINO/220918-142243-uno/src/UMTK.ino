#include <Arduino.h>
#include <EEPROM.h>

#include "slideNew.h"
#include "PCB_PinMap.h"
#include "HX711.h"
#include "setup.h"
#include "dispmeow.h"


void slideISR();
void PID_Control();
void Move_Down(long Control_Signal);
void Move_Up(long Control_Signal);


#define POWER_SENSE_SCALE 51.2
#define printWhileStopped 1
#define HEADER_TEXT "NEW_DATA\tSPEED\tPOSITION\tLOADCELL\tFEEDBACK_COUNT\tSTATE\tESTOP\tSTALL\tDIRECTION\tINPUT_VOLTAGE\tBT_FWD\tBT_BAK\tBT_TARE\tBT_START\tBT_AUX\n"


// EEPROM Constants
#define EEPROM_MAGIC_VALUE 0x7A8176B3
#define EEPROM_MAGIC_VALUE_ADDRESS 0x01
#define EEPROM_LC_DIVIDER_ADDRESS 0x05
#define EEPROM_LC_OFFSET_ADDRESS 0x09

byte SLIDE_BIT_COUNT = 0; // Count number of bits read
uint32_t SLIDE_DATA_BUFFER = 0; // Buffer To Shift Data Into
int32_t SLIDE_VALID_DATA = 0; // Valid data stored here
uint32_t SLIDE_LAST_BIT_TIME = 0; // Last time a bit was read, this handles start and if scale fall out of sync
long SLIDE_DATA_TIME = 0; // Last time a bit was read, this handles start and if scale fall out of sync
bool SLIDE_NEW_DATA = false;  // Stored if data is updated

typedef enum {down, up, press, release} ButtonState_t;
ButtonState_t startButton, stopButton, zeroButton, upButton, downButton, auxButton;

slide Slide(SLIDE_DATA, SLIDE_CLOCK);
HX711 LoadCell(LOADCELL_DATA, LOADCELL_CLOCK);

//Change this calibration factor as per your load cell once it is found you many need to vary it in thousands
long calibration_factor_load = 22025; //-106600 worked for my 40Kg max scale setup 
float calibration_factor_displacement = -98.9;

int lastSWITCH_STARTState = 0;
int loopcount = 0;
int dist_read_count = 0;
float set_speed = 2;
int max_control = 1023;
int min_control = 80;
long control_signal = set_speed/3 * 1023;
float dis_now = 0;
float dis_last = 0;
long t_now = 0;
long t_last = 0;
long t_last_PID;
long T_sample = 50;
long dt = 0;
float Load = 0;
float cur_speed = 0;
float total_error = 0;
float last_error;
float error;
bool control_direction = false;

int sevenseg_loop_count = 0;
int sevenseg_hold_time = 10;
unsigned long LC_divider = 0;
long LC_offset = 0;

float d_dist = 0.0;
long d_t = 0;

bool newLsData = false;
float powerInput = 0.0;

long pid_p = 0;
long pid_i = 0;
long pid_d = 0;
float Kp = 50;
float Ki = 0;  
float Kd = 0; 

enum UMTKStates_t {
  JOG_UP,
  JOG_DOWN,
  RUNNING,
  STANDBY,
  noChange,
};



enum sevseg {
  DIG1,
  DIG2,
  DIG3,
  DIG4,
  DIG_OFF
  } sevseg;


UMTKStates_t UMTKState = STANDBY;
UMTKStates_t UMTKNextState = noChange;

//=============================================================================================
//                         SETUP
//=============================================================================================
void setup() {
  
  cli(); //stop interrupts


  // #############
  // Pin Config
  // #############
  setPins();

  // #############
  // Setup Serial Logging
  // #############

  // Faster Baud is great because logging is blocking
  Serial.begin(250000);
  // Print Headers here once we figure out
  Serial.print(HEADER_TEXT);

  // #############
  // Setup Slide
  // #############
  attachInterrupt(digitalPinToInterrupt(SLIDE_CLOCK), slideISR, FALLING);
  Slide.set_scale(calibration_factor_displacement);
  Slide.tare(); //Reset the scale to 0


  // #############
  // Setup HX711
  // #############

  // // Check EEPROM if there is a stored value. Do this by verifying eeprom magic value
  // unsigned long eepromMagicRead = 0UL;
  // if (EEPROM.get(EEPROM_MAGIC_VALUE_ADDRESS, eepromMagicRead) == EEPROM_MAGIC_VALUE) {
  //   // eeprom magic match
  //   EEPROM.get(EEPROM_LC_DIVIDER_ADDRESS, LC_divider);
  //   EEPROM.get(EEPROM_LC_OFFSET_ADDRESS, LC_offset);
  // } 
  // else 
  // {
    long zero_factor_load = LoadCell.read_average(); //Get a baseline reading
    LC_offset = 0;
    LC_divider = calibration_factor_load;
  // }

  LoadCell.begin(LOADCELL_DATA, LOADCELL_CLOCK);
  LoadCell.set_scale(LC_divider);
  LoadCell.set_offset(LC_offset);
  LoadCell.tare(); //Reset the scale to 0


  digitalWrite(MOTOR_DISABLE, LOW);
  digitalWrite(DISP1_OE, LOW);
  digitalWrite(DISP2_OE, LOW);
  
  UMTKState = STANDBY;
  UMTKNextState = noChange;
  sevseg = DIG_OFF;

  // Enable Interrupts
  sei();
}
 
//==============u===============================================================================
//                         LOOP
//=============================================================================================
void loop() {

  Slide.set_scale(calibration_factor_displacement); //Adjust to this calibration factor

  {
    startButton = updateButtonState(SWITCH_START, startButton);
    stopButton = updateButtonState(SWITCH_STOP, stopButton);
    zeroButton = updateButtonState(SWITCH_ZERO, zeroButton);
    upButton = updateButtonState(SWITCH_MVUP, upButton);
    downButton = updateButtonState(SWITCH_MVDOWN, downButton);
    auxButton = updateButtonState(SWITCH_AUX, auxButton);
  }

  UMTKNextState = noChange;

  Read_Serial();

  // Determine next state
  Determine_Next_State();

  // Process State Machine Actions
  Transistion_State();
  

  // Read Loacell
  // Remove the if statement if you wish to print slower and only new new LoadCell value is available

  // Get input voltage
  powerInput = (float)(analogRead(VIN_SENSE)) / POWER_SENSE_SCALE;
  
  if (Slide.is_ready())
  {
    dis_now = Slide.get_units(1) / 1.096 ;
    t_now = SLIDE_DATA_TIME;

    d_t = t_now - t_last;
    d_dist = dis_now - dis_last;

    cur_speed = (1000*d_dist)/((double)(d_t));

    dis_last = dis_now;
    t_last = t_now;
    dist_read_count ++;
  }

  if (loopcount % 10 == 0)
  {
    // Calculate Speed From Slide Feedback
    if (LoadCell.is_ready()) {
      Load = fabs(LoadCell.get_units(1) * 9.8);
      newLsData = true;
    } else {
      newLsData = false;
    }
    Send_to_UI();
  }
  loopcount ++;

  
  if (dist_read_count % 2 == 0)
  {
    if (UMTKState == RUNNING)
    {
      PID_Control();
    }
    dist_read_count = 0;
  }

  Update_Display();

  
//
  //Print disp, force data to serial (so python can save to .csv file)

  /*
  Serial.print(t_now);
  Serial.print(", ");
  Serial.print(control_signal);
  Serial.print(", ");
  Serial.print(cur_speed);
  Serial.print(", ");
  Serial.print(-Slide.get_units(), 3);
  Serial.print(", ");
  Serial.println(-LoadCell.get_units(), 3);
  */

  /*
  if(Serial.available()){
    char temp = Serial.read();
    if(temp == 't'){
      LoadCell.tare();
      Slide.tare(); //Reset to zero
    }
  }
  */
  

}

// void Move_Up(long Control_Signal){
//     analogWrite(M_IN1, Control_Signal);
//     analogWrite(M_IN2, 0);
//     delay(300);
// }

// void Move_Down(long Control_Signal){
//     analogWrite(M_IN1, 0);
//     analogWrite(M_IN2, Control_Signal);
//     delay(300);  
// }

void inline tareAll()
{
  sevenSeg::refresh(5);
  LoadCell.tare();
  Slide.tare();
  Serial.println(" ========= TARE ==========");
  Serial.print(HEADER_TEXT);
}

void inline Update_Display()
{
  switch (sevseg){
    case DIG1:
        sevenSeg::refresh(0);
        sevseg = DIG2;
        delay(2);
        break;
        
    case DIG2:
        sevenSeg::refresh(1);
        sevseg = DIG3;
        delay(2);
        break;
        
    case DIG3:
        sevenSeg::refresh(2);
        sevseg = DIG4;
        delay(2);
        break;
        
    case DIG4:
        sevenSeg::refresh(3);
        sevseg = DIG_OFF;
        delay(2);
        break;

    case DIG_OFF:
        sevenSeg::refresh(5);
        sevenSeg::setInt( 1, abs ((int) round (dis_now * 10)), 1);
        sevenSeg::setInt( 2, abs ((int) round (Load * 10)), 1);
        sevseg = DIG1;
        break;
  }
}

void inline Determine_Next_State()
{
  switch (UMTKState){
    case JOG_UP:
    {
      if(upButton == up){
        UMTKNextState = STANDBY;
        break;
      }
      break;
    }

    case JOG_DOWN:
    {
      if(downButton == up){
        UMTKNextState = STANDBY;
        break;
      }
      break;
    }

    case STANDBY:
    {
      if(upButton == press || upButton == down){
        UMTKNextState = JOG_UP;
        break;
      }
      
      if(downButton == press || downButton == down){
        UMTKNextState = JOG_DOWN;
        break;
      }

      if(zeroButton == press){
        tareAll();
        UMTKNextState = noChange;
        break;
      }
      
      if(startButton == press){
        UMTKNextState = RUNNING;
        break;
      }
    }

    case RUNNING:
    {
      if(stopButton == press){
        UMTKNextState = STANDBY;
        break;
      }
      break;
    }
    
    case noChange:
      break;
  }

}

void inline Transistion_State()
{
  switch (UMTKNextState)
  {
    case noChange:
      break;

    case JOG_UP:
      analogWrite(M_IN1, 0);
      analogWrite(M_IN2, 1023);
      UMTKState = JOG_UP;
      break;

    case JOG_DOWN:
      analogWrite(M_IN1, 1023);
      analogWrite(M_IN2, 0);
      UMTKState = JOG_DOWN;
      break;

    case STANDBY:
      analogWrite(M_IN1, 1023);
      analogWrite(M_IN2, 1023);
      UMTKState = STANDBY;
      break;
    
    case RUNNING:
      UMTKState = RUNNING;
      break;
  }
  UMTKNextState = noChange;
}

void inline Send_to_UI()
{
  // Logging
  // Logging format
  // NEW_DATA SPEED POSITION LOADCELL FEEDBACK_COUNT STATE ESTOP STALL DIRECTION INPUT_VOLTAGE
  if (UMTKState != STANDBY || printWhileStopped) {  

    Serial.print(newLsData ? 1:0);
    Serial.print("\t");

    Serial.print(cur_speed); // Stepper Speed
    Serial.print("\t");
    Serial.print(dis_now); // Position
    Serial.print("\t");
    Serial.print(Load); // Load
    Serial.print("\t");
    Serial.print(0);  // Stepper feedback pos
    Serial.print("\t");
    Serial.print(UMTKState); // State
    Serial.print("\t");
    Serial.print(0); // eStop Input
    Serial.print("\t");
    Serial.print(0); // Stepper Stall
    Serial.print("\t");
    Serial.print(0); // Stepper Direction
    Serial.print("\t");

    Serial.print(powerInput);
    Serial.print("\t");
    
    Serial.print(upButton);
    Serial.print("\t");
    Serial.print(downButton);
    Serial.print("\t");
    Serial.print(zeroButton);
    Serial.print("\t");
    Serial.print(startButton);
    Serial.print("\t");
    Serial.print(auxButton);
    Serial.print("\t");

    
  #ifdef QAMODE
  // QAMODE
  if (buttonFwPressed) {  
    Serial.print("OK");
  } else {
    Serial.print("-");
  }
  Serial.print("\t");
  
  if (buttonBkPressed) {  
    Serial.print("OK");
  } else {
    Serial.print("-");
  }
  Serial.print("\t");
  
  if (buttonTarePressed) {  
    Serial.print("OK");
  } else {
    Serial.print("-");
  }
  Serial.print("\t");
  
  if (buttonStartPressed) {  
    Serial.print("OK");
  } else {
    Serial.print("-");
  }
  Serial.print("\t");
  
  if (buttonAuxPressed) {  
    Serial.print("OK");
  } else {
    Serial.print("-");
  }
  Serial.print("\t");
  
  if (eStopOff) {  
    Serial.print("OK");
  } else {
    Serial.print("-");
  }
  Serial.print("\t");
  
  if (eStopOn) {  
    Serial.print("OK");
  } else {
    Serial.print("-");
  }
  Serial.print("\t");

  #endif
    
    Serial.print("\n");
  }
}


void PID_Control(){
  
  if (t_now - t_last_PID > T_sample){
    dt = t_now - t_last_PID;
    t_last_PID = t_now;

    error = (set_speed - cur_speed);
    pid_p = Kp*error;
    pid_d = 0; //Kd*((error - last_error)/dt);
    pid_i = Ki*total_error;  

 /*   Serial.print("Control Parameters: ");
    Serial.print(pid_p);
    Serial.print(", ");
    Serial.print(pid_d);
    Serial.print(", ");
    Serial.println(pid_i);
*/
    last_error = error;
    total_error = error*dt + total_error;
  }
  control_signal = pid_p + pid_d + pid_i + 100;

  if (control_signal > 0)
  {
    control_direction = true;
  }
  else
  {
    control_direction = false;
    control_signal = -control_signal;
  }

  if (control_signal > max_control){
    control_signal = max_control;
  }
  else if(control_signal < min_control){
    control_signal = min_control;
  }

  
  if (control_direction)
  {
    analogWrite(M_IN1, 0);
    analogWrite(M_IN2, control_signal);
  }
  else
  {
    analogWrite(M_IN1, control_signal);
    analogWrite(M_IN2, 0);
  }

}


void Read_Serial()
{
  
  if (Serial.available()) {
    int incomingByte = Serial.read();
    Serial.print(incomingByte);

    if (incomingByte == 'v' || incomingByte == 'V') {
      // Set Speed Command
      float newSpeed = Serial.parseFloat();
      if (!isnan(newSpeed)) {
        set_speed = newSpeed;
      }
    }

    if (incomingByte == 'b' || incomingByte == 'B') {
      if (Serial.readStringUntil('\n') == "egin") {
        // Start Running
        if (UMTKState == STANDBY) {
          UMTKNextState = RUNNING;
        }
      }
    }
    if (incomingByte == 'c' || incomingByte == 'C') {      
      LC_divider = LoadCell.get_value(10)/49;
      LoadCell.set_scale(LC_divider);
      EEPROM.put(EEPROM_MAGIC_VALUE_ADDRESS, (unsigned long)EEPROM_MAGIC_VALUE);
      EEPROM.put(EEPROM_LC_DIVIDER_ADDRESS, LC_divider);
      EEPROM.put(EEPROM_LC_OFFSET_ADDRESS, LoadCell.get_offset());
    }

    if (incomingByte == 's' || incomingByte == 'S') {      
      if (UMTKState == RUNNING) {
        UMTKNextState = STANDBY;
      }
    }

    if (incomingByte == 't' || incomingByte == 'T') {
      if (Serial.readStringUntil('\n') == "are") {
        if (UMTKState != RUNNING) {
          tareAll();
        }
      }
    }
    
    // Other start symbols ignored
  }
}

// Read state of buttons and capture edges
ButtonState_t updateButtonState (int buttonToCheck, ButtonState_t lastState) {
  if (!digitalRead(buttonToCheck)) {
    switch (lastState) {
      case down:
        return down;
      case up:
        return press;
      case press:
        return down;
      case release:
        return press;
    }
  } else {
    switch (lastState) {
      case down:
        return release;
      case up:
        return up;
      case press:
        return release;
      case release:
        return up;
    }
  }
  return up;
}


//================================================================

// SLIDE CODE FOR NEW SLIDE

void slideISR() {
  // Immidiately Latch Bit for data
  bool this_bit = digitalRead(SLIDE_DATA);

  // Check if this is first bit in series or one of many bits
  uint32_t SLIDE_THIS_BIT_TIME = millis();
  if (SLIDE_THIS_BIT_TIME - SLIDE_LAST_BIT_TIME > 100 ) {
    // If a long time has passed this is the first bit
    SLIDE_DATA_BUFFER = 0; // Clear buffer ready for more bits
    SLIDE_BIT_COUNT = 0;
  }
  SLIDE_LAST_BIT_TIME = SLIDE_THIS_BIT_TIME;

  if (SLIDE_BIT_COUNT <= 23) {  // Check if a read is in progress, if it is this is timing sensitive
    SLIDE_BIT_COUNT ++; // Increment bit coutner
    if (!this_bit) { // incoming bit is 0, our logic is inverted
      SLIDE_DATA_BUFFER = SLIDE_DATA_BUFFER | 0x80000000; // Set LSB 
    }
    SLIDE_DATA_BUFFER = SLIDE_DATA_BUFFER >> 1; // Shift buffer by one bit
    if (SLIDE_BIT_COUNT == 23) { // This is last bit, do casting stuff
      SLIDE_DATA_BUFFER = SLIDE_DATA_BUFFER >> 8;
      if (SLIDE_DATA_BUFFER & 0x00100000) { // Check negative bit
        // negative
        SLIDE_VALID_DATA = 0 - (int32_t) (0x000FFFFF & SLIDE_DATA_BUFFER);
        SLIDE_DATA_TIME = millis();
        SLIDE_NEW_DATA = true;
      } else {
        // positive
        SLIDE_VALID_DATA = (int32_t)(0x000FFFFF & SLIDE_DATA_BUFFER);
        SLIDE_DATA_TIME = millis();
        SLIDE_NEW_DATA = true;
      }
      SLIDE_DATA_BUFFER = 0; // Clear buffer ready for more bits
      SLIDE_BIT_COUNT = 0;
     // Serial.println(round(SLIDE_VALID_DATA/6.5));
    }
  }
}
