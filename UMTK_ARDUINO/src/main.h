#include <Arduino.h>
#include <EEPROM.h>

#include <slideNew.h>
#include <HX711.h>
#include <setup.h>
#include <MAX7219.h>

#include <PCB_PinMap.h>
#include <button.h>

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
#define HEADER_TEXT "MILLIS\tDIRECTION\tPOSITION\tLOAD\tCUR_SPEED\tSET_SPEED\tSTATE\tMOT_F_AMPS\tMOT_B_AMPS\tBT_UP\tBT_DOWN\tBT_TARE\tBT_AUX\tIN_VOLTS\tVM_VOLTS\tLOOP_T\n"


// EEPROM Constants
#define EEPROM_MAGIC_VALUE 0x7A8176B3
#define EEPROM_MAGIC_VALUE_ADDRESS 0x00
#define EEPROM_LC_DIVIDER_ADDRESS 0x07
#define EEPROM_LC_OFFSET_ADDRESS 0x10

slide Slide(SLIDE_DATA, SLIDE_CLOCK);
HX711 LoadCell(LOADCELL_DATA, LOADCELL_CLOCK);
MAX7219 SevenSeg(DISP_CS);


float calibration_factor_displacement = -98.9;

int lastSWITCH_STARTState = 0;
int loopcount = 0;
int dist_read_count = 0;
float set_speed = 1;
float Load = 0;
float Load1 = 0;
float Load2 = 0;
float Load3 = 0;
float cur_speed = 0;
float total_error = 0;
float last_error;
float error;
bool control_direction = false;
int t_loop_this = 0;
int t_loop_last = 0;
float d_dist = 0.0;
long d_t = 0;
float dis_now = 0;
float dis_last = 0;

// Stall detection code
uint8_t stall_detect_counter = 0;
static constexpr uint8_t stall_detect_trip_count  = 100;
bool jog_lockout = false;

uint8_t serial_jog_counter = 255;
static constexpr uint8_t serial_jog_time = 250;

unsigned long LC_divider = 0;
long LC_offset = 0;

bool newLsData = false;
float power_volts = 0.0;
float vm_volts = 0.0;
float mot1_amps = 0.0;
float mot2_amps = 0.0;

unsigned long serial_last_send_t = 0;
unsigned long serial_last_send2_t = 0;
long serial_send_period = 100;

// PID Constants
long T_sample = 120;
float Kp = 20;
float Ki = 0.05;  
float Kd = 1; 
int max_control = 1023;
int min_control = 20;

// PID Vars
long pid_dt = 0;
float pid_dx = 0;
float pid_speed = 0;
long pid_p = 0;
long pid_i = 0;
long pid_d = 0;
long control_signal = set_speed/3 * 1023;
long t_now = 0;
long t_last = 0;
long pid_t_last = 0;
float pid_d_last = 0;

// LED Blink
unsigned long led_last_transition_t = 0;
long led_period = 1000;


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
  TARE,
};

UMTKStates_t UMTKState = STANDBY;
UMTKStates_t UMTKNextState = noChange;


enum RunDirection_t 
{
  UP,
  DOWN,
};

RunDirection_t run_direction = UP;

//=============================================================================================
//                         SETUP
//=============================================================================================
void setup();
//=============================================================================================
//                         LOOP
//=============================================================================================
void loop();
void tareAll();
void Update_Display();
void Determine_Next_State();
void Transistion_State();
void Send_to_UI();
void PID_Control();
void Read_Serial();
void Read_Slide();



//================================================================
// Slide ISR, this is to be invoked directly from main cpp
//================================================================
byte SLIDE_BIT_COUNT = 0; // Count number of bits read
uint32_t SLIDE_DATA_BUFFER = 0; // Buffer To Shift Data Into
int32_t SLIDE_VALID_DATA = 0; // Valid data stored here
uint32_t SLIDE_LAST_BIT_TIME = 0; // Last time a bit was read, this handles start and if scale fall out of sync
long SLIDE_DATA_TIME = 0; // Last time a bit was read, this handles start and if scale fall out of sync
bool SLIDE_NEW_DATA = false;  // Stored if data is updated

// SLIDE CODE FOR NEW SLIDE as of Aug 2024
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