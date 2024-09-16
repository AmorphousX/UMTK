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
  EEPROM.get(EEPROM_MAGIC_VALUE_ADDRESS, eepromMagicRead);
  // Reset mode, if AUX and START is pressed on power up, reset the Calibration
  if (digitalRead(SWITCH_START) == LOW && digitalRead(SWITCH_AUX) == LOW)
  {

    EEPROM.put(EEPROM_MAGIC_VALUE_ADDRESS, (unsigned long)0x00000000);
    EEPROM.put(EEPROM_LC_DIVIDER_ADDRESS, (unsigned long)0x00000000);
    EEPROM.put(EEPROM_LC_OFFSET_ADDRESS, (unsigned long)0x00000000);
    LC_offset = 0;
    LC_divider = FACTORY_CALIBRATION_DEFAULT;
    Serial.print("++++ CALIBRATION CLEARED WITH BUTTONS COMBO:\t");
    Serial.print(LC_divider);
    Serial.print("\t");
    Serial.println(LC_offset);
    delay(10);
  }
  else if (eepromMagicRead == EEPROM_MAGIC_VALUE)
  {
    // eeprom magic match
    EEPROM.get(EEPROM_LC_DIVIDER_ADDRESS, LC_divider);
    EEPROM.get(EEPROM_LC_OFFSET_ADDRESS, LC_offset);
    Serial.print("++++ Restored Calibration From EEPROM:\t");
    Serial.print(LC_divider);
    Serial.print("\t");
    Serial.println(LC_offset);
  } 
  else 
  {
    // eeprom magic no match
    LC_offset = 0;
    LC_divider = FACTORY_CALIBRATION_DEFAULT;

    Serial.print("++++ USING DEFAUT CAIBRATION:\t");
    Serial.print(LC_divider);
    Serial.print("\t");
    Serial.println(LC_offset);
    delay(100);
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

  // Enable LED Indicator
  #ifdef LED_BLINKABLE
    pinMode(LED_BUILTIN, OUTPUT);
    led_period = 1500;
    led_last_transition_t = millis();
  #endif
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
  vm_volts = (float)(analogRead(VMOT_SENSE)) / VSENSE_iK;
  mot1_amps = (float)analogRead(MOTOR_ISENSE_1) / VMOT_ISENSE_iK;
  mot2_amps = (float)analogRead(MOTOR_ISENSE_2) / VMOT_ISENSE_iK;
  
  Read_Slide();

  if (UMTKState == RUNNING)
  {
    PID_Control();
  }

  // Calculate Speed From Slide Feedback
  if (LoadCell.is_ready()) {
    // Very basic filter to filter data
    Load3 = Load2;
    Load2 = Load1;
    Load1 = LoadCell.get_units(1);
    Load = (Load1 + Load2 + Load3)/3;
    newLsData = true;
  } else {
    newLsData = false;
  }

  // Force a serial test for TARE state so UI gets updated
  if (millis() >= (unsigned long)(serial_last_send_t + serial_send_period)
      || UMTKState == TARE)
  {
    serial_last_send_t = millis();
    Send_to_UI();
    serial_last_send2_t = millis();
  }

// Blink LED to indicate status
#ifdef LED_BLINKABLE
  if (led_period < 0)
  {
    //  If negative value, LED always on
    digitalWrite(LED_BUILTIN, HIGH); 
  }
  else if (led_period == 0)
  {
    //  If 0 LED always off
    digitalWrite(LED_BUILTIN, LOW); 

  }
  else if (millis() >= (unsigned long)(led_last_transition_t + led_period))
  {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    led_last_transition_t = millis();
  }
#endif

  if ((mot1_amps + mot2_amps) > STALL_AMPS_THREASHOLD)
  {
    if (stall_detect_counter < 254)
    {
      stall_detect_counter ++;
    }
  }
  else
  {
    stall_detect_counter = 0;
  }

  Update_Display();
  loopcount ++;
}

void tareAll()
{
  Serial.println(" ========= TARE ==========");
  LoadCell.tare();
  Slide.tare();
  dis_now = 0;
  dis_last = 0;
  Load = 0;
  Load1 = 0;
  Load2 = 0;
  Load3 = 0;
  Serial.print(HEADER_TEXT);
}

void Update_Display()
{
  SevenSeg.writeNumeric(0, abs((int)(Load)));
  
  if (dis_now < -99.9 || dis_now > 999.9)
  {
    SevenSeg.writeNumeric(1, int(dis_now));
  }
  else
  {
    SevenSeg.writeNumeric(1, int(dis_now*10),1);
  }
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
  }
}

void Determine_Next_State()
{
  switch (UMTKState){
    case JOG_UP:
    {
      if (stall_detect_counter  > stall_detect_trip_count)
      {
        jog_lockout = true;
        UMTKNextState = STANDBY;
        break;
      }
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
      if (stall_detect_counter  > stall_detect_trip_count)
      {
        jog_lockout = true;
        UMTKNextState = STANDBY;
        break;
      }
      if (serial_jog_counter < serial_jog_time)
      {
        // If jog is invoked from serial, we hold it for a bit
        serial_jog_counter++;
        UMTKNextState = JOG_DOWN;
      }
      else
      {
        // If jog timer expired, it's up to the button
        if(downButton == up){
          UMTKNextState = STANDBY;
          break;
        }
      }
      break;
    }

    case STANDBY:
    {
      if(auxButton == press){
        if (run_direction == UP)
        {
          run_direction = DOWN;
        }
        else
        {
          run_direction = UP;
        }
      }

      // Clear jog logout, wait for user to release button before allowing jog again after stall
      if (upButton == up && downButton == up)
      {
        jog_lockout = false;
      }

      if(!jog_lockout && (upButton == press || upButton == down)){
        UMTKNextState = JOG_UP;
        break;
      }
      
      if(!jog_lockout && (downButton == press || downButton == down)){
        UMTKNextState = JOG_DOWN;
        break;
      }

      if(zeroButton == press){
        UMTKNextState = TARE;
        break;
      }
      
      if(startButton == press){
        UMTKNextState = RUNNING;
        break;
      }
    }

    case RUNNING:
    {
      if (stall_detect_counter  > stall_detect_trip_count)
      {
        UMTKNextState = STANDBY;
        break;
      }
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

    case TARE:
    {
      tareAll();
      UMTKNextState = STANDBY;
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
      analogWrite(M_IN2, 1023);
      UMTKState = JOG_UP;
      led_period = -1;
      break;

    case JOG_DOWN:
      analogWrite(M_IN1, 1023);
      analogWrite(M_IN2, 0);
      UMTKState = JOG_DOWN;
      led_period = -1;
      break;

    case STANDBY:
      analogWrite(M_IN1, 1023);
      analogWrite(M_IN2, 1023);
      UMTKState = STANDBY;
      led_period = 0;
      break;
    
    case RUNNING:
      // Clear PID Integral
      total_error = 0.0;
      pid_d_last = dis_now;
      pid_t_last = t_now;
      UMTKState = RUNNING;
      led_period = 100;
      break;
    
    case TARE:
      UMTKState = TARE;
      led_period = -1;
      break;
    
    default:
      break;
  }
  UMTKNextState = noChange;
}

void Send_to_UI()
{
  // Logging
  if (UMTKState != STANDBY || printWhileStopped) {  
    Serial.print(millis()); //Print a time counter
    Serial.print("\t");
    Serial.print(run_direction); //Run Direction
    Serial.print("\t");
    Serial.print(dis_now); // Position
    Serial.print("\t");
    Serial.print(Load); // Load
    Serial.print("\t");
    Serial.print(cur_speed); // Current Speed
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
    Serial.print(millis() - serial_last_send2_t);         // Loop Time
    Serial.print("\n");
  }
}


void PID_Control(){
  
  if (t_now - pid_t_last > T_sample){
    pid_dt = t_now - pid_t_last;
    pid_dx = dis_now - pid_d_last;
    pid_d_last = dis_now;
    pid_t_last = t_now;

    pid_speed = abs((pid_dx*1000) / (double)pid_dt);

    error = (set_speed - pid_speed);
    pid_p = Kp*error;
    pid_d = (last_error - error)*100*Kd/pid_dt;
    pid_i = Ki*total_error;  

    last_error = error;
    total_error = error*(double)pid_dt + total_error;
    // clamp intergral so it doesn't cause long running issues
    total_error = constrain(total_error, -1e7, 1e7);

    control_signal = pid_p + pid_d + pid_i;
    
    if (control_signal > max_control){
      control_signal = max_control;
    }
    else if(control_signal < min_control){
      control_signal = min_control;
    }

    if (run_direction == UP)
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
      LC_offset = abs(LoadCell.get_offset());
      EEPROM.put(EEPROM_MAGIC_VALUE_ADDRESS, (unsigned long)EEPROM_MAGIC_VALUE);
      EEPROM.put(EEPROM_LC_DIVIDER_ADDRESS, LC_divider);
      EEPROM.put(EEPROM_LC_OFFSET_ADDRESS, LC_offset);
      Serial.print("Saved Calibration Factors to EEPROM: ");
      Serial.print(LC_divider);
      Serial.print("\t");
      Serial.print(LC_offset);
    }

    if (incomingByte == 's' || incomingByte == 'S') {
      // Stop Running and stop hault serial jog
      serial_jog_counter = 255;
      UMTKNextState = STANDBY;
    }

    if (incomingByte == 't' || incomingByte == 'T') {
      if (Serial.readStringUntil('\n') == "are") {
        if (UMTKState != RUNNING) {
          UMTKNextState = TARE;
        }
      }
    }

    // q for reverse of p, set direction to down
    if (incomingByte == 'q' || incomingByte == 'Q')
    {
      UMTKNextState = STANDBY;
      run_direction = DOWN;
    }

    // p for pull, set direction to up
    if (incomingByte == 'p' || incomingByte == 'P')
    {
      UMTKNextState = STANDBY;
      run_direction = UP;
    }

    // r for setting serial data rate
    if (incomingByte == 'r' || incomingByte == 'R')
    {
      long newRate = Serial.parseInt();
      if (newRate > 0 && newRate <= 200)
      {
        serial_send_period = 1000/newRate;
      }
    }
    // Other start symbols ignored
  }
}