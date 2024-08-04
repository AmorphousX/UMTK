#include <main.h>

//=============================================================================================
//                         SETUP
//=============================================================================================
void setup() {

  cli(); //stop interrupts
  t_loop_last = millis();
  t_loop_this = millis();

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
  // Check EEPROM if there is a stored value. Do this by verifying eeprom magic value
  unsigned long eepromMagicRead = 0UL;
  if (EEPROM.get(EEPROM_MAGIC_VALUE_ADDRESS, eepromMagicRead) == EEPROM_MAGIC_VALUE)
  {
    // eeprom magic match
    EEPROM.get(EEPROM_LC_DIVIDER_ADDRESS, LC_divider);
    EEPROM.get(EEPROM_LC_OFFSET_ADDRESS, LC_offset);
  } 
  else 
  {
    // long zero_factor_load = LoadCell.read_average(); //Get a baseline reading
    LC_offset = 0;
    LC_divider = calibration_factor_load;
  }

  LoadCell.begin(LOADCELL_DATA, LOADCELL_CLOCK);
  LoadCell.set_scale(LC_divider);
  LoadCell.set_offset(LC_offset);
  LoadCell.tare(); //Reset the scale to 0

  // #############
  // Setup MOTOR
  // #############
  //  Motor Mode Pin:
  //  - High: Phase / EN
  //  - LOW: PWM
  //  - 200K to GND, +-5%, Independent
  //  Latched upon exiting sleep
  //
  //  nSLEEP low puts driver to sleep

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
  SevenSeg.setIntensity(10);
  SevenSeg.writeNumeric(0,(int)0);
}
 
//=============================================================================================
//                         LOOP
//=============================================================================================

void loop() {

  t_loop_last = t_loop_this;
  t_loop_this = millis();

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

  // Read Analogue inputs
  power_volts = (float)(analogRead(VIN_SENSE)) / VSENSE_iK;
  vm_volts = (float)(analogRead(VIN_SENSE)) / VSENSE_iK;
  mot1_amps = (float)analogRead(MOTOR_ISENSE_1) / VMOT_ISENSE_iK;
  mot2_amps = (float)analogRead(MOTOR_ISENSE_2) / VMOT_ISENSE_iK;
  
  Read_Slide();

  if (dist_read_count % 2 == 0)
  {
    if (UMTKState == RUNNING)
    {
      PID_Control();
    }
    dist_read_count = 0;
  }

  // Calculate Speed From Slide Feedback
  if (LoadCell.is_ready()) {
    // Very basic filter to filter data
    Load = (Load + fabs(LoadCell.get_units(1) * 9.8)) / 2;
    newLsData = true;
  } else {
    newLsData = false;
  }

  if (loopcount % 150 == 0)
  {

    Send_to_UI();
  }
  loopcount ++;

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

void Read_Slide()
{
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
}

void Determine_Next_State()
{
  switch (UMTKState){
    case JOG_UP:
    {
      if (serial_jog_counter < serial_jog_time)
      {
        // If jog is invoked from serial, we hold it for a bit
        serial_jog_counter++;
        UMTKNextState = JOG_UP;
      }
      else
      {
        if(upButton == up){
          UMTKNextState = STANDBY;
          break;
        }
      }
      break;
    }

    case JOG_DOWN:
    {
      if (serial_jog_counter < serial_jog_time)
      {
        // If jog is invoked from serial, we hold it for a bit
        serial_jog_counter++;
        UMTKNextState = JOG_DOWN;
      }
      // if(downButton == release){
      //   UMTKNextState = STANDBY;
      //   break;
      // }
      else
      {
        // If jog timer expired, it's up to the button
        if(downButton == up){
          UMTKNextState = STANDBY;
          break;
        }
      }
      // if(downButton == release){
      //   UMTKNextState = STANDBY;
      //   break;
      // }
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
    Serial.print(set_speed); // Commanded Speed
    Serial.print("\t");
    Serial.print(UMTKState); // State
    Serial.print("\t");
    Serial.print(mot1_amps); // Motor Phase 1 Amps
    Serial.print("\t");
    Serial.print(mot2_amps); // Motor Phase 2 Amps
    Serial.print("\t");
    Serial.print(upButton);  // Up Button State
    Serial.print("\t");
    Serial.print(downButton); // Down Button State
    Serial.print("\t");
    Serial.print(zeroButton); // Tare
    Serial.print("\t");
    Serial.print(startButton); // Start Button
    Serial.print("\t");
    Serial.print(auxButton);   // Aux Button
    Serial.print("\t");
    Serial.print(power_volts);   // Input Voltage
    Serial.print("\t");
    Serial.print(vm_volts);   // Motor Voltage
    Serial.print("\t");
    Serial.print(t_loop_this - t_loop_last);         // Loop Time
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
    float newSpeed = 0.0f;
    int incomingByte = Serial.read();

    if (incomingByte == 'v' || incomingByte == 'V') {
      // Set Speed Command
      newSpeed = Serial.parseFloat();
      if (!isnan(newSpeed)) {
        set_speed = newSpeed;
      }
    }
    if (incomingByte == 'U') {
      // Up
      if (UMTKState == JOG_UP || UMTKState == STANDBY ) {
        UMTKNextState = JOG_UP;
        serial_jog_counter = 0;
      }
    }
    if (incomingByte == 'D') {
      // Down
      if (UMTKState == JOG_DOWN || UMTKState == STANDBY ) {
        UMTKNextState = JOG_DOWN;
        serial_jog_counter = 0;
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
      // Calibrate Command
      float calLoad = Serial.parseFloat();
      LC_divider = LoadCell.get_value(10)/calLoad;
      LoadCell.set_scale(LC_divider);
      EEPROM.put(EEPROM_MAGIC_VALUE_ADDRESS, (unsigned long)EEPROM_MAGIC_VALUE);
      EEPROM.put(EEPROM_LC_DIVIDER_ADDRESS, LC_divider);
      EEPROM.put(EEPROM_LC_OFFSET_ADDRESS, LoadCell.get_offset());
    }

    if (incomingByte == 's' || incomingByte == 'S') {
      // Stop Running and stop hault serial jog
      serial_jog_counter = 255;
      UMTKNextState = STANDBY;
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
