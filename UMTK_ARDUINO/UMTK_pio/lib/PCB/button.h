#pragma once

#if ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

typedef enum {down, up, press, release} ButtonState_t;
ButtonState_t startButton, zeroButton, upButton, downButton, auxButton;

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

