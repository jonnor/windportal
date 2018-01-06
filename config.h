
#include <Adafruit_NeoPixel.h>
#define HAVE_ADAFRUIT_NEOPIXEL

#if 0
// FIXME: makes sketch to big on Arduino Leonardo
#include <ArduinoHttpClient.h>
#define HAVE_ARDUINO_HTTP
#define TINY_GSM_MODEM_SIM800

#include <TinyGsmClient.h>
#define HAVE_TINYGSM
TinyGsm modem(Serial1);
TinyGsmClient client(modem);
static const char server[] = "cdn.rawgit.com";
static const int  port     = 443;
HttpClient http(client, server, port);
#endif
