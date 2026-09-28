from time import sleep

from gpiozero import AngularServo, Button
from gpiozero.pins.pigpio import PiGPIOFactory


factory = PiGPIOFactory(host="localhost")

servo = AngularServo(
    18,                          # Physical pin 12
    pin_factory=factory,
    min_angle=-90,
    max_angle=90,
    min_pulse_width=0.001,
    max_pulse_width=0.002
)

left_button = Button(
    17,                          # Physical pin 11
    pin_factory=factory,
    pull_up=True,
    bounce_time=0.03
)

right_button = Button(
    27,                          # Physical pin 13
    pin_factory=factory,
    pull_up=True,
    bounce_time=0.03
)

centre_button = Button(
    22,                          # Physical pin 15
    pin_factory=factory,
    pull_up=True,
    bounce_time=0.03
)


angle = 0.0

minimum_angle = -90.0
maximum_angle = 90.0

# Movement configuration
movement_speed = 120.0     # Degrees per second
update_interval = 0.02     # 50 updates per second
movement_step = movement_speed * update_interval

servo.angle = angle

print("Servo controller started")
print("Hold LEFT or RIGHT to move continuously")
print("Press CENTRE to return smoothly to 0°")
print("Press Ctrl+C to stop")

try:
    while True:
        moved = False

        if left_button.is_pressed and not right_button.is_pressed:
            angle = max(minimum_angle, angle - movement_step)
            moved = True

        elif right_button.is_pressed and not left_button.is_pressed:
            angle = min(maximum_angle, angle + movement_step)
            moved = True

        elif centre_button.is_pressed:
            # Move smoothly toward zero
            if angle > movement_step:
                angle -= movement_step
            elif angle < -movement_step:
                angle += movement_step
            else:
                angle = 0.0

            moved = True

        if moved:
            servo.angle = angle
            print(
                f"\rAngle: {angle:6.1f}°",
                end="",
                flush=True
            )

        sleep(update_interval)

except KeyboardInterrupt:
    print("\nServo controller stopped")

finally:
    servo.detach()

    servo.close()
    left_button.close()
    right_button.close()
    centre_button.close()

    factory.close()