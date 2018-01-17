
#include <Adafruit_NeoPixel.h>
#include <Servo.h>

// Fill the dots one after the other with a color
void barGraph(Adafruit_NeoPixel *strip,
    uint16_t position, uint8_t offset, uint32_t oncolor, uint32_t offcolor) {

    for(uint16_t i=offset; i<strip->numPixels(); i++) {
        strip->setPixelColor(i, offcolor);
    }
    const uint16_t stop = min(offset+position, strip->numPixels());
    for(uint16_t i=offset; i<stop; i++) {
        strip->setPixelColor(i, oncolor);
    }
}


const int8_t SERVO_PIN = 9;
const int8_t DISPLAY_PIN = 6;
const int8_t DISPLAY_LEDS = 24;
const int8_t LIVE_PIN = 13;

Adafruit_NeoPixel strip(DISPLAY_LEDS, DISPLAY_PIN, NEO_GRB + NEO_KHZ800);
Servo servo;

const auto ON_COLOR = strip.Color(255,0,0);
const auto OFF_COLOR = strip.Color(5,5,5);

// TODO: generate
static const uint16_t speeds[] = {
    10,
    0,
    20,
    40,
}; 
static const size_t speeds_length = (sizeof(speeds)/sizeof(speeds[0]));
static const uint16_t speed_max = 100;

void setup() {
    strip.begin();
    strip.show();
    strip.setBrightness(255);

    servo.attach(SERVO_PIN);
    servo.write(0);

    pinMode(LIVE_PIN, OUTPUT);
}

void loop() {
  static int pos = 0;

  const auto speed = speeds[pos];
  
  const int pixels = map(speed, 0, speed_max, 0, DISPLAY_LEDS);
  barGraph(&strip, pixels, 0, ON_COLOR, OFF_COLOR);
  strip.show();
  
  const int pwm = map(speed, 0, speed_max, 0, 1024);
  analogWrite(LIVE_PIN, pwm);

  if (pos > speeds_length) {
    pos = 0;
  }
  pos += 1;
  delay(500);
}


