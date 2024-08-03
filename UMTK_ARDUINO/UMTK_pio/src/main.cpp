#include <main.h>

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

  // Check EEPROM if there is a stored value. Do this by verifying eeprom magic value
  unsigned long eepromMagicRead = 0UL;
  if (EEPROM.get(EEPROM_MAGIC_VALUE_ADDRESS, eepromMagicRead) == EEPROM_MAGIC_VALUE) {
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
  SevenSeg.setIntensity(2);
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
    float newSpeed = 0.0f;
    int incomingByte = Serial.read();
    Serial.print(incomingByte);

    if (incomingByte == 'v' || incomingByte == 'V') {
      // Set Speed Command
      newSpeed = Serial.parseFloat();
      if (!isnan(newSpeed)) {
        set_speed = newSpeed;
      }
    }
    if (incomingByte == 'D') {
      // Set Speed Command
      newSpeed = Serial.parseFloat();
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