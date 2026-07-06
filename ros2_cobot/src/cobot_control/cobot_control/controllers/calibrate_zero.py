"""Re-zero each servo's physical straight-up pose to read as 180 degrees (tick 2048).

Run this only once the arm is physically positioned exactly where you want
the new zero/180-degree reference to be.
"""

from scservo_sdk import SMS_STS_OFS_L
import joint_controller as jc

TARGET_TICK = 2048  # 180 degrees, mid-scale of the 0-4095 range


def encode_correction(value):
    # STS3215 "position correction" register: bit 11 is a sign flag,
    # the low 11 bits (0-2047) hold the magnitude.
    sign_bit = 0x800 if value < 0 else 0
    magnitude = min(abs(value), 2047)
    return sign_bit | magnitude


def zero_servo(ctrl, servo_id):
    raw, result, error = ctrl.servo.ReadPos(servo_id)

    correction = TARGET_TICK - raw
    ctrl.servo.unLockEprom(servo_id)
    ctrl.servo.write2ByteTxRx(servo_id, SMS_STS_OFS_L, encode_correction(correction))
    ctrl.servo.LockEprom(servo_id)

    new_pos, result, error = ctrl.servo.ReadPos(servo_id)
    print(f"servo {servo_id}: was {raw}, now reads {new_pos} (target {TARGET_TICK})")

    if abs(new_pos - TARGET_TICK) > 5:
        # sign convention guess was wrong, try the opposite direction
        ctrl.servo.unLockEprom(servo_id)
        ctrl.servo.write2ByteTxRx(servo_id, SMS_STS_OFS_L, encode_correction(-correction))
        ctrl.servo.LockEprom(servo_id)
        new_pos, result, error = ctrl.servo.ReadPos(servo_id)
        print(f"servo {servo_id}: retried opposite sign, now reads {new_pos} (target {TARGET_TICK})")


if __name__ == "__main__":
    ctrl = jc.JointController()
    for servo_id in ctrl.ids:
        zero_servo(ctrl, servo_id)
    ctrl.close()
