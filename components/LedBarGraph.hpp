
#ifdef HAVE_ADAFRUIT_NEOPIXEL
#include <Adafruit_NeoPixel.h>


// Fill pixels up to @position
void
barGraph(Adafruit_NeoPixel *strip,
         uint16_t position, uint32_t oncolor, uint32_t offcolor)
{
  const uint16_t N = strip->numPixels(); 

#if 1
  for(uint16_t i=0; i<strip->numPixels(); i++) {
    strip->setPixelColor(i, offcolor);
  }
  const uint16_t stop = min(position, strip->numPixels());
  for(uint16_t i=0; i<stop; i++) {
    strip->setPixelColor(i, oncolor);
  }
#endif

  strip->show();


}
#endif

/* microflo_component yaml
name: LedBarGraph
description: Custom does whatever you want
inports:
  in:
    type: number
    description: ""
outports:
  out:
    type: all
    description: ""
microflo_component */
class LedBarGraph : public SingleOutputComponent {
private:
#ifdef HAVE_ADAFRUIT_NEOPIXEL
    Adafruit_NeoPixel strip;
#endif
    uint32_t offcolor;
    uint32_t oncolor;
public:
    LedBarGraph()
    {
        // TODO: split into two parts, setting up neopixel, and doing the bargraph?
        const int8_t pin = 6;
        const int8_t leds = 60;
#ifdef HAVE_ADAFRUIT_NEOPIXEL
        strip = Adafruit_NeoPixel(leds, pin, NEO_GRB + NEO_KHZ800);
        oncolor = strip.Color(255,0,0);
        offcolor = strip.Color(10,10,10);

        strip.begin();
        strip.show(); // FIXME: remove?
#endif
    }

    virtual void process(Packet in, MicroFlo::PortId port) {
        using namespace LedBarGraphPorts;
        if (port == InPorts::in && in.isData()) {
            const int pos = in.asInteger();
#ifdef HAVE_ADAFRUIT_NEOPIXEL
            const long before = micros(); 
            Adafruit_NeoPixel *s = &strip;
            barGraph(s, pos, oncolor, offcolor);
            const long after = micros();
#endif
            send(Packet(after-before), OutPorts::out);
            //send(in, OutPorts::out);
        }
    }
};