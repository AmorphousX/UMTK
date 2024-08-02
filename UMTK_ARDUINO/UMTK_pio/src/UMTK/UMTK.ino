#include <Arduino.h>
#include <EEPROM.h>

#include "slideNew.h"
#include "PCB_PinMap.h"
#include "HX711.h"
#include "setup.h"
#include "MAX7219.h"


void inline slideISR();
void inline PID_Control();
void inline Move_Down(long Control_Signal);
void inline Move_Up(long Control_Signal);
void inline tareAll();
void inline Update_Display();
void inline Determine_Next_State();
void inline Transistion_State();
void inline Send_to_UI();

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
ButtonState_t startButton, zeroButton, upButton, downButton, auxButton;

slide Slide(SLIDE_DATA, SLIDE_CLOCK);
HX711 LoadCell(LOADCELL_DATA, LOADCELL_CLOCK);
MAX7219 SevenSeg(DISP_CS);


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


// String[] MMTKstateEnum = {"Running", "Stopped", "Hold", "Jog Forward", "Jog Back", "Fast Jog Forward", "Fast Jog Back", " - "};
enum UMTKStates_t {
  RUNNING,
  STANDBY,
  UNUSED1,
  JOG_UP,
  JOG_DOWN,
  UNUSED2,
  UNUSED3,
  noChange,
};


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
  digitalWrite(SLIDE_CLOCK_DIR, LOW);
  digitalWrite(SLIDE_DATA_DIR, LOW);
  attachInterrupt(digitalPinToInterrupt(SLIDE_CLOCK), slideISR, RISING);
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

  // #############
  // Setup MOTOR
  // #############
  digitalWrite(MOTOR_nSLEEP, LOW);
  digitalWrite(MOTOR_MODE, HIGH);
  delay(1);
  digitalWrite(MOTOR_nSLEEP, HIGH);
  
  UMTKState = STANDBY;
  UMTKNextState = noChange;
  // Enable Interrupts
  sei();
  
  // #############
  // Setup Display
  // #############
  SevenSeg.init(true);
  SevenSeg.setIntensity(8);
  SevenSeg.writeNumeric(0,(int)0);
}
 
//=============================================================================================
//                         LOOP
//=============================================================================================

void loop() {

  Slide.set_scale(calibration_factor_displacement); //Adjust to this calibration factor

  {
    startButton = updateButtonState(SWITCH_START, startButton);
    zeroButton = updateButtonState(SWITCH_TARE, zeroButton);
    upButton = updateButtonState(SWITCH_JOGUP, upButton);
    downButton = updateButtonState(SWITCH_JOGDOWN, downButton);
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
  powerInput = (float)(analogRead(VIN_SENSE)) / VSENSE_iK;
  
  if (Slide.is_ready())
  {
    dis_now = Slide.get_units() ;
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
}

void tareAll()
{
  LoadCell.tare();
  Slide.tare();
  Serial.println(" ========= TARE ==========");
  Serial.print(HEADER_TEXT);
}

void Update_Display()
{
  SevenSeg.writeNumeric(0, (int)(Load));
  SevenSeg.writeNumeric(1, int(dis_now*10),1);
//  SevenSeg.writeNumeric(1, (int)(millis()/100), 1);
}

void Determine_Next_State()
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
      if(upButton == press){
        UMTKNextState = STANDBY;
        break;
      }
      if(downButton == press){
        UMTKNextState = STANDBY;
        break;
      }
      if(auxButton == press){
        UMTKNextState = STANDBY;
        break;
      }
      break;
    }
    
    case noChange:
      break;
  }

}

void Transistion_State()
{
  switch (UMTKNextState)
  {
    case noChange:
      break;

    case JOG_UP:
      analogWrite(M_IN1, 0);
      analogWrite(M_IN2, 500);
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

void Send_to_UI()
{
//  Serial.print((float)analogRead(VIN_SENSE)/18.6181818182);
//  Serial.print(",");
//  Serial.print((float)analogRead(VMOT_SENSE)/18.6181818182);
//  Serial.print(",");
  Serial.print(cur_speed); // Stepper Speed
  Serial.print(",");
  Serial.print((float)analogRead(MOTOR_ISENSE_1)/126.603636364);
  Serial.print(",");
  Serial.println((float)analogRead(MOTOR_ISENSE_2)/126.603636364);

  return;
  // Logging
  // Logging format
  // NEW_DATA SPEED POSITION LOADCELL FEEDBACK_COUNT STATE ESTOP STALL DIRECTION INPUT_VOLTAGE
  if (UMTKState != STANDBY || printWhileStopped) {  

    Serial.print(dis_now); // Position
    Serial.print("\t");
    Serial.print(Load); // Load
    Serial.print("\t");
    Serial.print(cur_speed); // Stepper Speed
    Serial.print("\t");
    Serial.print(UMTKState); // State
    Serial.print("\t");
    Serial.print(Load); // Load
    Serial.print("\t");
    Serial.print((float)analogRead(MOTOR_ISENSE_1)/126.603636364);  // Stepper feedback pos
    Serial.print("\t");
    Serial.print((float)analogRead(MOTOR_ISENSE_2)/126.603636364); // Stepper Stall
    Serial.print("\t");
//    Serial.print(0); // Stepper Direction
//    Serial.print("\t");
//
//    Serial.print(powerInput);
//    Serial.print("\t");
//    
//    Serial.print(upButton);
//    Serial.print("\t");
//    Serial.print(downButton);
//    Serial.print("\t");
//    Serial.print(zeroButton);
//    Serial.print("\t");
//    Serial.print(startButton);
//    Serial.print("\t");
//    Serial.print(auxButton);
//    Serial.print("\t");
    
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
    if (incomingByte == 'D') {
      // Set Speed Command
      float newSpeed = Serial.parseFloat();
      if (UMTKState == STANDBY) {
        UMTKNextState = RUNNING;
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
  if (SLIDE_THIS_BIT_TIME - SLIDE_LAST_BIT_TIME > 20 ) {
    // If a long time has passed this is the first bit
    SLIDE_DATA_BUFFER = 0; // Clear buffer ready for more bits
    SLIDE_BIT_COUNT = 0;
  } 
  SLIDE_LAST_BIT_TIME = SLIDE_THIS_BIT_TIME;
  
  //  Slide Data Structure, 6 Nibbles
  //  dddd dddd dddd dddd xxxx Sxxx 
  //  LSB first, S is sign bit
  //  Sign bit seems to be bit number 21

  if (SLIDE_BIT_COUNT <= 24) {  // Check if a read is in progress
    SLIDE_BIT_COUNT ++; // Increment bit coutner
    if (this_bit) {
      SLIDE_DATA_BUFFER = SLIDE_DATA_BUFFER | 0x80000000; // Set LSB 
    }
    SLIDE_DATA_BUFFER = SLIDE_DATA_BUFFER >> 1; // Shift buffer by one bit

    // Bit 23 is the last bit, we perfectly shifted everything now
    // Data after this doesn't matter
    if (SLIDE_BIT_COUNT == 23)
    {
        SLIDE_DATA_BUFFER = SLIDE_DATA_BUFFER >> 8;
        if (SLIDE_DATA_BUFFER & 0x00100000) { // Check sign bit
          // negative
          SLIDE_VALID_DATA = 0 - (int32_t)(0x000FFFFF & SLIDE_DATA_BUFFER);
          SLIDE_DATA_TIME = millis();
          SLIDE_NEW_DATA = true;
        } else {
          // positive
          SLIDE_VALID_DATA = (int32_t)(0x000FFFFF & SLIDE_DATA_BUFFER);
          SLIDE_DATA_TIME = millis();
          SLIDE_NEW_DATA = true;
        }
    }
  }
}
