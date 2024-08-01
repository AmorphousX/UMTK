# pragma once

#include "PCB_PinMap.h"

#if ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

class slide
{
  private:


    byte PD_SCK;  // Power Down and Serial Clock Input Pin
    byte DOUT;    // Serial Data Output Pin
    byte GAIN;    // amplification factor
    long OFFSET = 0;  // used for tare weight
    float SCALE = 1;  // used to return weight in grams, kg, ounces, whatever
  
	public:
 
		// define clock and data pin, channel
		slide(byte dout, byte pd_sck);

		slide();


		virtual ~slide();

		// Allows to set the pins and gain later than in the constructor
		void begin(byte dout, byte pd_sck);

		// check if slide is ready
		// from the datasheet: When output data is not ready for retrieval, digital output pin DOUT is high. Serial clock
		// input PD_SCK should be low. When DOUT goes to low, it indicates data is ready for retrieval.
		bool is_ready();

		// waits for the chip to be ready and returns a reading
		long read();

		// returns get_value() divided by SCALE, that is the raw value divided by a value obtained via calibration
		// times = how many readings to do
		double get_units();

		// set the OFFSET value for tare weight; times = how many times to read the tare value
		void tare();

		// set the SCALE value; this value is used to convert the raw data to "human readable" data (measure units)
		void set_scale(float scale = 1.f);

		// get the current SCALE
		float get_scale();

		// set OFFSET, the value that's subtracted from the actual reading (tare weight)
		void set_offset(long offset = 0);

		// get the current OFFSET
		long get_offset();
};
