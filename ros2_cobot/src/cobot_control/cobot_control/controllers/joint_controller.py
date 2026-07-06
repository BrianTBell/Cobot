"""Joint controller implementation placeholder."""

from glob import glob
from serial import SerialException
from serial.tools import list_ports
from scservo_sdk import COMM_SUCCESS, PortHandler, sms_sts
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import utilities as utility
import math
import time


class JointController:
    def __init__(self, baud=1000000):
        self.ids = [1,2,3,4]
        self.port, self.servo = self._connect(baud)

        self.joint_limits = [(math.degrees(lo), math.degrees(hi)) for lo, hi in utility.load_joint_limits()]


    def setPosition(self, position, units='deg', speed=1500, acc=10):
        for servo_id, angle, in zip(self.ids, position):
            # Get joint limits
            joint_min = self.joint_limits[servo_id-1][0]
            joint_max = self.joint_limits[servo_id-1][1]
            # Set joints per limits
            angle = max(joint_min, min(joint_max, angle))
            angle = round((angle + 180) / 360 * 4095) # -180 deg -> 0, 0 deg -> 2048, 180 deg -> 4095
            self.servo.WritePosEx(servo_id, angle, speed, acc)


    def getJointPositions(self, units='deg'):
        positions = []
        for servo_id in self.ids:
            pos, result, error = self.servo.ReadPos(servo_id)
            if result != COMM_SUCCESS:
                raise RuntimeError(f"Failed to read position for servo {servo_id}")
            if units == 'deg': positions.append(round(pos / 4095 * 360 - 180,4))
            else: positions.append(round(pos / 4095 * 2 * math.pi - math.pi,4))
        return positions


    def close(self):
        self.port.closePort()


    def _connect(self, baud, audit=False):
        # Get all non bluetooth ports
        ports = [
            p.device
            for p in list_ports.comports()
            if "Bluetooth" not in p.description
        ] + glob("/dev/serial/by-id/*")

        # For all of those ports ping servos.
        for name in ports:
            port = PortHandler(name)
            try:
                opened = port.openPort() and port.setBaudRate(baud)
                if audit: print(f"Success on port:\t {name}")
            except:
                if audit: print(f"\tFailure on port:\t {name}")
                continue
            if opened:
                servo = sms_sts(port)
                if all(servo.ping(servo_id)[1] == COMM_SUCCESS for servo_id in self.ids):
                    return port, servo
                port.closePort()
        raise RuntimeError("Could not find STS3215 servos")


if __name__ == "__main__":
    ctrl = JointController()
    looking_away = [90,60,135,120]
    sitting = [0,60,135,120]
    standing = [0, -30, 120, 0]
    ctrl.setPosition(standing)
    ctrl.close()