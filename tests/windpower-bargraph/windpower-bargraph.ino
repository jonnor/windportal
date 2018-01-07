#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

#define PIN 6

Adafruit_NeoPixel strip = Adafruit_NeoPixel(60, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  // This is for Trinket 5V 16MHz, you can remove these three lines if you are not using a Trinket
  #if defined (__AVR_ATtiny85__)
    if (F_CPU == 16000000) clock_prescale_set(clock_div_1);
  #endif
  // End of trinket special code

  strip.begin();
  strip.show(); // Initialize all pixels to 'off'
  strip.setBrightness(255);
}

void loop() {
  //colorWipe(strip.Color(255, 0, 0), 50); // Red
  static int pos = 0;

  barGraph(pos*2, 0, strip.Color(255,255,255), strip.Color(0,00,10));
  barGraph(pos*2, 24, strip.Color(255,255,255), strip.Color(0,0,10));
  strip.show();
  
  pos += 1;
  if (pos > 12) {
    pos = 0;
  }
  delay(50);
}

// Fill the dots one after the other with a color
void barGraph(uint8_t position, uint8_t offset, uint32_t oncolor, uint32_t offcolor) {
  for(uint16_t i=offset; i<strip.numPixels(); i++) {
    strip.setPixelColor(i, offcolor);
  }
  for(uint16_t i=offset; i<offset+position; i++) {
    strip.setPixelColor(i, oncolor);
  }
}
;
