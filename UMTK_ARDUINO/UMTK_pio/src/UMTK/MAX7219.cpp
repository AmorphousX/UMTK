#include "MAX7219.h"

// Private

MAX7219::MAX7219(uint8_t cs)
{
    CS = cs;
    digitalWrite(CS, HIGH);
}

void
MAX7219::setDisplayEnable(bool enable)
{
    SPI.beginTransaction(SPISettings(SPI_DATARATE, MSBFIRST, SPI_MODE0));
    digitalWrite(CS, LOW);
    SPI.transfer(ADDR_SHUTDOWN);
    SPI.transfer(0x01 & enable);
    digitalWrite(CS, HIGH);
    SPI.endTransaction();
}

void
MAX7219::setDisplayTest(bool enable)
{
    SPI.beginTransaction(SPISettings(SPI_DATARATE, MSBFIRST, SPI_MODE0));
    digitalWrite(CS, LOW);
    SPI.transfer(ADDR_TEST);
    SPI.transfer(0x01 & enable);
    digitalWrite(CS, HIGH);
    SPI.endTransaction();
}

void
MAX7219::setMode(uint8_t mode)
{
    SPI.beginTransaction(SPISettings(SPI_DATARATE, MSBFIRST, SPI_MODE0));
    digitalWrite(CS, LOW);
    SPI.transfer(ADDR_MODE);
    SPI.transfer(mode);
    digitalWrite(CS, HIGH);
    SPI.endTransaction();
}


void
MAX7219::setScanLim(uint8_t scanlim)
{
    SPI.beginTransaction(SPISettings(SPI_DATARATE, MSBFIRST, SPI_MODE0));
    digitalWrite(CS, LOW);
    SPI.transfer(ADDR_SCANLIM);
    SPI.transfer(scanlim);
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

    SPI.beginTransaction(SPISettings(SPI_DATARATE, MSBFIRST, SPI_MODE0));
    for (int i = 0; i < len; i++)
    {
        digitalWrite(CS, LOW);
        SPI.transfer(ADDR_DIG0 + digit_start + i);
        SPI.transfer(displayBuf[digit_start + i]);
        digitalWrite(CS, HIGH);
    }
    SPI.endTransaction();

    return len;

}

uint8_t
MAX7219::updateDisplay()
{
    return updateDisplay(0, 8);
}


//  Public

void
MAX7219::init(bool initSPI)
{
    // Startup SPI, 
    // sequence, enable driver, write test for 1 second
    if (initSPI)
    {
        SPI.begin();
    }
    setIntensity(4);
    setDisplayEnable(true);
    setMode(MODE_DECODEALL);
    setScanLim(0x07);
    setDisplayTest(true);
    delay(1000);
    setDisplayTest(false);
}

void
MAX7219::writeNumeric(uint8_t display_id, float val)
{
    // Unimplimented
}

void
MAX7219::writeNumeric(uint8_t display_id, int val, uint8_t decimal_bits)
{
    uint8_t digit_start = 0;
    if (display_id > 0)
    {
        digit_start = 4;
    }

    if (val >= 10000)
    {
        displayBuf[digit_start] = 0x89;
        displayBuf[digit_start+1] = 0x89;
        displayBuf[digit_start+2] = 0x89;
        displayBuf[digit_start+3] = 0x89;
    }
    else if (val <= -1000)
    {
        displayBuf[digit_start] = 0x8A; // 0x0A is "-"
        displayBuf[digit_start+1] = 0x89;
        displayBuf[digit_start+2] = 0x89;
        displayBuf[digit_start+3] = 0x89;
    }
    else
    {
        // Negative Number
        if (val < 0)
        {
            displayBuf[digit_start] =   0x0A; // 0x0A is "-"
            int tempval = 0;
            for (int i = 1; i < 4; i++)
            {
                tempval =  (val / (4-1)*10) % 10;
                // If this value is a zero, and previous digit was a ignored zero
                // We turn this digit off also
                if (!(MAX7219_WITH_LEADING_ZEROS && tempval))
                {
                    if (displayBuf[digit_start+i-1] & 0x8)
                    {
                        displayBuf[digit_start+i] = tempval | 0x08;
                    }
                }
                else
                {
                    displayBuf[digit_start+i] = tempval;
                }
            }

            // Last digit is never turned off
            displayBuf[digit_start+3] = displayBuf[digit_start+3] & 0xF;

        }
        // Positive
        else
        {
            displayBuf[digit_start] =   (val / 1000) % 10;
            displayBuf[digit_start+1] = (val / 100) % 10;
            displayBuf[digit_start+2] = (val / 10) % 10;
            displayBuf[digit_start+3] = val % 10;
        }

        // Add decimals
        displayBuf[digit_start] = displayBuf[digit_start] & 0x0F | (decimal_bits & 0x08) << 4;
        displayBuf[digit_start+1] = displayBuf[digit_start+1] & 0x0F | (decimal_bits & 0x04) << 5;
        displayBuf[digit_start+2] = displayBuf[digit_start+2] & 0x0F | (decimal_bits & 0x02) << 6;
        displayBuf[digit_start+3] = displayBuf[digit_start+3] & 0x0F | (decimal_bits & 0x01) << 7;
    }
    updateDisplay();
    return;
}

uint8_t
MAX7219::setIntensity(uint8_t intensity)
{
    SPI.beginTransaction(SPISettings(SPI_DATARATE, MSBFIRST, SPI_MODE0));
    digitalWrite(CS, LOW);
    SPI.transfer(ADDR_INTENSITY);
    SPI.transfer(intensity);
    digitalWrite(CS, HIGH);
    SPI.endTransaction();
    return (0x0F & intensity);
}
