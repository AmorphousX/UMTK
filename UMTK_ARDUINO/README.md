# UMTK Arduino Firmware

The UMTK arduino firmware is a Platform IO Project. Platform IO is a Visual Studio Code Plugin.

## Setup Project for Dev

To develop for UMTK arduino;

Install Visual Studio Code:
https://code.visualstudio.com/download

Install Platform IO Plugin:
https://platformio.org/install/ide?install=vscode

After installing, open the project folder in Platform IO:
`UMTK\UMTK_ARDUINO\UMTK_pio`


## Serial Data Schema

The firmware will continuously send data out from the main serial port:

Baud: 250000

Data is tab seperated values, with these columns:

- POSITION
- LOAD
- CUR_SPEED
- SET_SPEED
- STATE
- MOTOR_F_AMPS
- MOTOR_R_AMPS
- BT_UP
- BT_DOWN
- BT_TARE
- BT_AUX
- LOOP_T

### Field Definitons:
All values are send over serial as strings. 
Data should be parsed from string into the apporiate types

| Column         | Data Type    | Units         | Description                                  |
| -------------- | ------------ | ------------- | -------------------------------------------  |
| POSITION       | Float        | Milimeters    | Position offset from zero point. Milimeters  |
| LOAD           | Float        | Newtons       | Loadcell Force from Current Calibration      |
| CUR_SPEED      | Float        | mm/s          | Current Speed                                |
| SET_SPEED      | Float        | mm/s          | Commanded Speed                              |
| STATE          | Int          | State Enum    | State Enum, See Below                        |
| MOTOR_F_AMPS   | Float        | Amps          | Motor Forward Current                        |
| MOTOR_R_AMPS   | Float        | Amps          | Motor Reverse Current                        |
| BT_UP          | Int          | Button Enum   | Button Enum, See Below                       |
| BT_DOWN        | Int          | Button Enum   | Button Enum, See Below                       |
| BT_TARE        | Int          | Button Enum   | Button Enum, See Below                       |
| BT_AUX         | Int          | Button Enum   | Button Enum, See Below                       |
| LOOP_T         | Int          | Miliseconds   | Time elapsed for this control loop           |


### State Enum Definitions
| Enum Value    | State             |
| ------------- | ----------------- |
| 0             | Running           |
| 1             | Standby, Idle     |
| 2             | Reserved          |
| 3             | Jog Up            |
| 4             | Jog Down          |
| 5             | Reserved          |
| 6             | Reserved          |
| 7             | Reserved          |


### Button Enum Definitions
| Enum Value    | State             |
| ------------- | ----------------- |
| 0             | Held Down         |
| 1             | Released          |
| 2             | Just Pressed      |
| 3             | Just Released     |


## Serial Control Interface

In addition to outputting data, the firmware continuously send data out from the main serial port:

Baud: 250000

Serial Commands:
Commands vary in length. By default there is no line ending character in the command.
Some commands require a line ending character, they are denoted by `\n` in the command column.

| Action            | Command               | Parameter(s)      | Description                    |
| ----------------- | --------------------- | ----------------  | ------------------------------ |
| Set Speed         | `V <new_speed>`       | float (32bit)     | Set commanded speed, mm/s      |
| Jog Up            | `U`                   | none              | Jog Up, Machine will jog for ~100ms after command. Send command continuously to jog longer distance |
| Jog DOWN          | `D`                   | none              | Jog Up, Machine will jog for ~100ms after command. Send command continuously to jog longer distance |
| Start Running     | `Begin\n`             | none              | Start Running Continuously At Commanded Speed |
| Calibrate Load    | `C <calibration_load>` | float (32bit)    | Calibrate Loadcell, Calibration Values are persisted in EEPROM Supply The Refence load in Newtons  |
| Stop              | `S`                   | none              | Stop UMTK if it is running mode |
| Tare              | `Tare\n`                | none              | Tare Load and Position, Resets position and load to zero |
