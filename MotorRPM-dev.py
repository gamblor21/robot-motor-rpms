import board
import time
from adafruit_crickit import crickit
from digitalio import DigitalInOut, Direction

class MotorRPM(object):
    def __init__(self, motor, rpm_sensor):
        self._motor = motor
        self._rpm_sensor = rpm_sensor
        self._target_rpm = 0
        self._motor.throttle = 0
        self._last_sensor_value = True
        self._last_sensor_time = time.monotonic_ns()
        self._last_rpm = 0
        self._last_throttle_adjust = time.monotonic()
        self._rpm_avg_list = [0.0, 0.0, 0.0, 0.0, 0.0]
        self._rpm_avg = 0.0
        self._revs = 0

    def set_rpm(self, rpm):
        if rpm >= 0 and rpm < 300:
            self._target_rpm = rpm

    def update_RPM(self):
        if self._rpm_sensor.value != self._last_sensor_value:
            self._last_sensor_value = not self._last_sensor_value

            if (self._last_sensor_value == False):
                elapsedtime = time.monotonic_ns() - self._last_sensor_time
                self._last_sensor_time = time.monotonic_ns()

                if elapsedtime == 0:
                    print('M1 Sensor wrong')
                else:
                    rpm = 60 / (elapsedtime/1000000000)
                    rpm = rpm / 5
                    if rpm > 300:
                        print('RPM out of bounds')
                    else:
                        self._last_rpm = rpm
                        self._rpm_avg_list.pop()
                        self._rpm_avg_list.insert(0, rpm)
                        self._rpm_avg = 0.0
                        for x in self._rpm_avg_list:
                            self._rpm_avg += x
                        self._rpm_avg /= 5
                        self._revs += 0.2

                        print((rpm,self._motor.throttle, self._rpm_avg))


        elapsedtime = time.monotonic() - self._last_throttle_adjust
        if elapsedtime > 0.1:
            self._last_throttle_adjust = time.monotonic()

            diff_rpm = abs(self._rpm_avg - self._target_rpm)
            if diff_rpm > 2:
                adjustment = 0
                if (diff_rpm > 90):
                    adjustment = 0.5
                    delay = 0.4
                elif (diff_rpm > 50):
                    adjustment = 0.2
                    delay = 0.3
                elif (diff_rpm > 20):
                    adjustment = 0.05
                    delay = 0.2
                elif (diff_rpm > 10):
                    adjustment = 0.025
                    delay = 0.2
                else:
                    adjustment = 0.005
                    delay = 0.2

                self._last_throttle_adjust += delay
                print((self._motor.throttle, adjustment))

                #print('Adjusting m1 rpm')
                if (self._rpm_avg > self._target_rpm):
                    self._motor.throttle = max(0.0, self._motor.throttle - adjustment)
                    #m1spd = m1spd - 0.005
                else:
                    self._motor.throttle = min(1.0, self._motor.throttle + adjustment)
                    #m1spd = m1spd + 0.005


print("Going")

m1 = crickit.dc_motor_2
m2 = crickit.dc_motor_1

targetspeed = 0
targetrpms = 0

m1spd = targetspeed

#m1.throttle = 1
#time.sleep(0.01)
#m1.throttle = m1spd

close1 = DigitalInOut(board.D6)
close1.direction = Direction.INPUT

close2 = DigitalInOut(board.D5)
close2.direction = Direction.INPUT

lastvalue1 = True
lasttime1 = time.monotonic()
statustime = time.monotonic()

m1revs = 0

rpm1 = -1
lastrpmchange = time.monotonic()

motor = MotorRPM(crickit.dc_motor_2, close1)
motor2 = MotorRPM(crickit.dc_motor_1, close2)

while True:
    motor.update_RPM()
    motor.set_rpm(113)

    motor2.update_RPM()
    motor2.set_rpm(113)


    if (time.monotonic() - statustime) > 3.0:
        print("*** STATUS ***")
        #print(m1.throttle)
        #print(m2.throttle)
        print((motor._revs,motor._rpm_avg,m1.throttle))
        print((motor2._revs,motor2._rpm_avg,m2.throttle))
        print("*** ****** ***")
        statustime = time.monotonic()