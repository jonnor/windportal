
#ifdef HAVE_SERVO
#include <Servo.h>

#else
#warning "Missing Servo library"
#endif

/* microflo_component yaml
name: ServoWrite
description: Control a servo
inports:
  in:
    type: number
    description: "Where to move servo to, in degrees"
    triggering: true
  pin:
    type: number
    description: "Pin servo is connected on"
outports:
  out:
    type: all
    description: ""
microflo_component */
class ServoWrite : public SingleOutputComponent {
private:
#ifdef HAVE_SERVO
    Servo servo;
#endif
public:
    ServoWrite()
    {
    }

    virtual void process(Packet in, MicroFlo::PortId port) {
        using namespace ServoWritePorts;

        if (port == InPorts::in && in.isData()) {
            const int pos = in.asInteger();
#ifdef HAVE_SERVO
            servo.write(pos);
#endif
            send((long)pos, OutPorts::out);
        } else if (port == InPorts::pin) {
            const int pin = in.asInteger();
#ifdef HAVE_SERVO
            servo.attach(pin);
#endif
        }
    }
};
