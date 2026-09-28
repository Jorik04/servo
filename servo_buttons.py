from time import sleep

from gpiozero import AngularServo, Button
from gpiozero.pins.pigpio import PiGPIOFactory


# Connect to the pigpio daemon
factory = PiGPIOFactory(host="localhost")


# Servo signal: GPIO18, physical pin 12
servo = AngularServo(
    18,
    pin_factory=factory,
    min_angle=-90,
    max_angle=90,
    min_pulse_width=0.001,
    max_pulse_width=0.002
)


# Buttons connect between their GPIO and GND
left_button = Button(
    17,                     # Physical pin 11
    pin_factory=factory,
    pull_up=True,
    bounce_time=0.05
)

right_button = Button(
    27,                     # Physical pin 13
    pin_factory=factory,
    pull_up=True,
    bounce_time=0.05
)

centre_button = Button(
    22,                     # Physical pin 15
    pin_factory=factory,
    pull_up=True,
    bounce_time=0.05
)


# Movement settings
angle = 0
minimum_angle = -45
maximum_angle = 45
movement_step = 1

servo.angle = angle
print("Servo controller started")
print("Left: GPIO17 | Right: GPIO27 | Centre: GPIO22")
print("Press Ctrl+C to stop")

try:
    while True:
        if left_button.is_pressed:
            angle -= movement_step
            angle = max(angle, minimum_angle)

            servo.angle = angle
            print(f"\rAngle: {angle}°   ", end="", flush=True)

        elif right_button.is_pressed:
            angle += movement_step
            angle = min(angle, maximum_angle)

            servo.angle = angle
            print(f"\rAngle: {angle}°   ", end="", flush=True)

        elif centre_button.is_pressed:
            angle = 0
            servo.angle = angle

            print("\rAngle: 0°   ", end="", flush=True)

        sleep(0.08)

except KeyboardInterrupt:
    print("\nServo controller stopped")

finally:
    servo.detach()

    servo.close()
    left_button.close()
    right_button.close()
    centre_button.close()

    factory.close()
