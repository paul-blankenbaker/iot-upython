import time
import machine

class SpeedController:

    def __init__(self, pin, freq=50, usMin=1000, usMax=2000):
        self.pin = machine.Pin(pin, machine.Pin.OUT)
        self.pwm = machine.PWM(self.pin, freq=freq, duty=0)
        self.freq = freq
        self.usMin = usMin
        self.usMax = usMax

    def setDuty(self, duty):
        """ Set how long the pulse is held high in usecs. """
        if (duty <= 0):
            self.disable()
            return
        print("Changing duty to:", duty, "usecs")
        us = min(self.usMax, max(self.usMin, duty))
        duty = us * 1024 * self.freq // 1000000
        self.pwm.duty(duty)

    def setPower(self, power):
        duty = (((power + 1.0) / 2.0 * (self.usMax - self.usMin)) + self.usMin)
        print("power:", power, "  duty:", duty)
        self.setDuty(int(duty))

    def disable(self):
        self.pwm.duty(0)

    def calibrate(self, cnt):
        sleepSecs = 1.0
        for i in range(1, cnt):
            self.setPower(1.0)
            time.sleep(sleepSecs)
            self.setPower(-1.0)
            time.sleep(sleepSecs)
            self.setPower(0.0)
            time.sleep(sleepSecs)

