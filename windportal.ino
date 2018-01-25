
#include "./data.h"

static const size_t speeds_length = (sizeof(speeds)/sizeof(speeds[0]));
static const int16_t speed_max = 32767;

#include <Adafruit_NeoPixel.h>
#include <Servo.h>

// Fill the dots one after the other with a color
void barGraph(Adafruit_NeoPixel *strip,
    uint16_t position, uint8_t offset) {

    for(uint16_t i=offset; i<strip->numPixels(); i++) {
        const uint32_t offcolor = off_colors[i];
        strip->setPixelColor(i, offcolor);
    }
    const uint16_t stop = min(offset+position, strip->numPixels());
    for(uint16_t i=offset; i<stop; i++) {
        const uint32_t oncolor = on_colors[i];
        strip->setPixelColor(i, oncolor);
    }
}


const int8_t SERVO_PIN = 9;
const int8_t DISPLAY_PIN = 6;
const int8_t DISPLAY_LEDS = 24;
const int8_t LIVE_PIN = 11;
const int8_t TRIGGER_PIN = 7;
const int8_t MOTOR_ENABLE_PIN = 5;

const int durationMillis = 12000;
const int timestepMillis = durationMillis / speeds_length;

Adafruit_NeoPixel strip(DISPLAY_LEDS, DISPLAY_PIN, NEO_GRB + NEO_KHZ800);
Servo servo;

int beufortScale(int16_t mps) {
  for (int i=1; i<12; i++) {
    if (mps > beufort_thresholds[i-1] && mps < beufort_thresholds[i]) {
      return i;
    }
  }
  return 0;
}

void set_position(int pos, bool motor_enable) {
  //Serial.print("pos=");
  //Serial.println(pos);
  
  const auto speed = speeds[pos];

  const bool motor_on = motor_enable and (speed > 0);
  digitalWrite(MOTOR_ENABLE_PIN, motor_on);

  const int pixels = 2*(1+beufortScale(speed));
  barGraph(&strip, pixels, 0);
  strip.show();
  const int servo_pos = constrain(map(speed, 0, speed_max, 0, 180), 0, 180);
  servo.write((motor_enable) ? servo_pos : 0);

  const int pwm = constrain(map(speed, 0, speed_max, 0, 1023), 0, 1023);
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
  static bool motor_enabled = false;
  
  const bool pressed = !digitalRead(TRIGGER_PIN);
  if ((pressed and not was_pressed)) {
      pos = 0;
      motor_enabled = true;
  }

  if (pos == speeds_length) {
    pos = 0;
    motor_enabled = false;
  }

  set_position(pos, motor_enabled);
  pos += 1;
  delay(timestepMillis);
  
  was_pressed = pressed;
}


