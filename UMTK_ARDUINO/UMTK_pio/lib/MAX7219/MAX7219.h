#pragma once

#if ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#include "SPI.h"

#define MAX7219_WITH_LEADING_ZEROS 0

class MAX7219
{
    private:
        uint8_t CS;

        static constexpr uint8_t ADDR_NOOP = 0x00;
        static constexpr uint8_t ADDR_DIG0 = 0x01;
        static constexpr uint8_t ADDR_MODE = 0x09;
        static constexpr uint8_t ADDR_INTENSITY = 0x0A;
        static constexpr uint8_t ADDR_SCANLIM = 0x0B;
        static constexpr uint8_t ADDR_SHUTDOWN = 0x0C;
        static constexpr uint8_t ADDR_TEST = 0x0F;

        static constexpr long SPI_DATARATE = 10000000;

        inline void setDisplayEnable(bool enable);
        inline void setDisplayTest(bool enable);
        inline void setScanLim(uint8_t scanlim);

        inline uint8_t updateDisplay(uint8_t digit_start, uint8_t len);
        inline uint8_t updateDisplay();
        inline void setMode(uint8_t mode);

        char displayBuf[8] = {0};

    public:
        MAX7219(uint8_t cs);
        void init(bool initSPI = true);
        uint8_t setIntensity(uint8_t intensity);
        void  writeNumeric(uint8_t display_id, float val);
        void  writeNumeric(uint8_t display_id, int val, uint8_t decimal_location = 0x00);

        static constexpr uint8_t MODE_NODECODE = 0x00;
        static constexpr uint8_t MODE_DECODEALL = 0xFF;

};
