#include <Arduino.h>
#include "slideNew.h"


slide::slide(byte dout, byte pd_sck) {
	begin(dout, pd_sck);
}

slide::slide() {
}

slide::~slide() {
}

void slide::begin(byte dout, byte pd_sck) {
	PD_SCK = pd_sck;
	DOUT = dout;

	pinMode(PD_SCK, INPUT);
	pinMode(DOUT, INPUT);

}

bool slide::is_ready() {
	return SLIDE_NEW_DATA;
}

long slide::read() {
	SLIDE_NEW_DATA = false;
	return SLIDE_VALID_DATA;
}

double slide::get_units() {
	return (read() - OFFSET)/SCALE;
}

void slide::tare() {
	set_offset(read());
}

void slide::set_scale(float scale) {
	SCALE = scale;
}

float slide::get_scale() {
	return SCALE;
}

void slide::set_offset(long offset) {
	OFFSET = offset;
}

long slide::get_offset() {
	return OFFSET;
}
