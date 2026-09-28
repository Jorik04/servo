from time import monotonic, sleep

from gpiozero import AngularServo, Button
from gpiozero.pins.pigpio import PiGPIOFactory
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306


# --------------------------------------------------
# OLED setup
# --------------------------------------------------

oled_serial = i2c(port=1, address=0x3C)

oled = ssd1306(
    oled_serial,
    width=128,
    height=64
)


def display_angle(angle):
    marker = int((angle + 90) / 180 * 127)
    marker = max(2, min(125, marker))

    with canvas(oled) as draw:
        draw.text(
            (18, 5),
            "SERVO ANGLE",
            fill="white"
        )

        draw.text(
            (38, 27),
            f"{angle:+.0f} deg",
            fill="white"
        )

        # Angle indicator
        draw.line(
            (2, 55, 125, 55),
            fill="white"
        )

        draw.line(
            (64, 51, 64, 59),
            fill="white"
        )

        draw.rectangle(
            (marker - 2, 52, marker + 2, 58),
            fill="white"
        )


# --------------------------------------------------
# GPIO and servo setup
# --------------------------------------------------

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


# --------------------------------------------------
# Movement settings
# --------------------------------------------------

angle = 0.0

minimum_angle = -90.0
maximum_angle = 90.0

movement_speed = 180.0
update_interval = 0.02
movement_step = movement_speed * update_interval

last_oled_update = 0.0

servo.angle = angle
display_angle(angle)

print("Servo and OLED controller started")
print("Press Ctrl+C to stop")


# --------------------------------------------------
# Main loop
# --------------------------------------------------

try:
    while True:
        moved = False

        if left_button.is_pressed and not right_button.is_pressed:
            angle = max(
                minimum_angle,
                angle - movement_step
            )
            moved = True

        elif right_button.is_pressed and not left_button.is_pressed:
            angle = min(
                maximum_angle,
                angle + movement_step
            )
            moved = True

        elif centre_button.is_pressed:
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

            # Update OLED no more than 10 times per second
            current_time = monotonic()

            if current_time - last_oled_update >= 0.1:
                display_angle(angle)
                last_oled_update = current_time

        sleep(update_interval)


except KeyboardInterrupt:
    print("\nController stopped")


finally:
    servo.detach()
    oled.clear()

    servo.close()
    left_button.close()
    right_button.close()
    centre_button.close()

    factory.close()