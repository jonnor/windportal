#include <Adafruit_WS2801.h>
#define HAVE_ADAFRUIT_WS2801

#if 0
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
