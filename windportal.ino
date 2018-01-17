
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
const int8_t TRIGGER_PIN = 7;
const int8_t MOTOR_ENABLE_PIN = 5;

Adafruit_NeoPixel strip(DISPLAY_LEDS, DISPLAY_PIN, NEO_GRB + NEO_KHZ800);
Servo servo;

const auto ON_COLOR = strip.Color(255,0,0);
const auto OFF_COLOR = strip.Color(5,5,5);

// TODO: generate
static const uint16_t speeds[] = {
    0,
    1,
    10,
    20,
    40,
    70,
    90,
    100,
    0,
    0,
};
static const size_t speeds_length = (sizeof(speeds)/sizeof(speeds[0]));
static const uint16_t speed_max = 100;

void set_position(int pos) {
  //Serial.print("pos=");
  //Serial.println(pos);
  
  const auto speed = speeds[pos];

  digitalWrite(MOTOR_ENABLE_PIN, speed > 0);

  const int pixels = map(speed, 0, speed_max, 0, DISPLAY_LEDS);
  barGraph(&strip, pixels, 0, ON_COLOR, OFF_COLOR);
  strip.show();
  const int servo_pos = map(speed, 0, speed_max, 0, 180); 
  servo.write(servo_pos);

  const int pwm = map(speed, 0, speed_max, 0, 1024);
  analogWrite(LIVE_PIN, pwm);
}

void setup() {
    strip.begin();
    strip.show();
    strip.setBrightness(255);

    servo.attach(SERVO_PIN);
    servo.write(0);

    pinMode(LIVE_PIN, OUTPUT);
    pinMode(MOTOR_ENABLE_PIN, OUTPUT);
    pinMode(TRIGGER_PIN, INPUT_PULLUP);
}

void loop() {
  static int pos = 0;
  static bool was_pressed = true;
  static bool playing = false;
  
  const bool pressed = !digitalRead(TRIGGER_PIN);
  if (playing or (pressed and not was_pressed)) {
      playing = true;
    
      if (pos == speeds_length) {
        pos = 0;
        playing = false;
      }
      set_position(pos);
      pos += 1;
      delay(1000);
  }
  was_pressed = pressed;
}


