#include "MAX7219.h"

// Private

void
MAX7219::MAX7219(uint8_t cs)
{
    CS = cs;
    digitalWrite(CS, HIGH);
}

void
MAX7219::setDisplayEnable(bool enable)
{
    SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE0));
    digitalWrite(CS, LOW);
    SPI.transfer(ADDR_SHUTDOWN);
    SPI.transfer(0x01 & enable);
    digitalWrite(CS, HIGH);
    SPI.endTransaction();
}

void
MAX7219::setDisplayTest(bool enable)
{
    SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE0));
    digitalWrite(CS, LOW);
    SPI.transfer(ADDR_TEST);
    SPI.transfer(0x01 & enable);
    digitalWrite(CS, HIGH);
    SPI.endTransaction();
}

void
MAX7219::setMode(uint8_t mode)
{
    SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE0));
    digitalWrite(CS, LOW);
    SPI.transfer(ADDR_MODE);
    SPI.transfer(mode);
    digitalWrite(CS, HIGH);
    SPI.endTransaction();
}

uint8_t
MAX7219::updateDisplay(uint8_t digit_start, uint8_t len)
{
    if (digit_start >= 8)
    {
        return 0;
    }

}



//  Public

void
MAX7219::begin(bool initSPI)
{
    // Startup SPI, 
    // sequence, enable driver, write test for 1 second
    if (initSPI)
    {
        SPI.begin()
    }
}

void
MAX7219::writeNumeric(uint8_t display_id, float val)
{

}

void
MAX7219::writeNumeric(uint8_t display_id, int val)
{
    uint8_t digit_start = display_id < 3;
    if (val > 10000)
    {
        
    }
}

uint8_t
MAX7219::setIntensity(uint8_t intensity)
{
    SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE0));
    digitalWrite(CS, LOW);
    SPI.transfer(ADDR_INTENSITY);
    SPI.transfer(intensity);
    digitalWrite(CS, HIGH);
    SPI.endTransaction();
    return (0x0F & intensity)
}
