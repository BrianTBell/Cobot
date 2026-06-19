from scservo_sdk import *
import time

PORT = "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B79031799-if00"
BAUD = 1000000

port = PortHandler(PORT)
servo = sms_sts(port)

assert port.openPort(), "failed to open port"
assert port.setBaudRate(BAUD), "failed to set baudrate"




def parse_deg(deg):
    # parse bad inputs
    if deg <0: deg = 0
    if deg > 360: deg = 360

    min_idx, max_idx = 0, 4095

    perc_rot = deg / (360)
    idx = int(round(max_idx*perc_rot,0))

    return idx



def move(id, pos, speed=3000, acc=50):
    servo.WritePosEx(id, pos, speed, acc)


try:
    for id in range(1, 5):
        model, result, error = servo.ping(id)
        assert result != COMM_RX_CORRUPT, "multiple motors have the same ID"
        assert result == COMM_SUCCESS, f"motor {id} not found"

    idx = parse_deg(0)

    move(1, idx)
    move(2, idx)
    move(3, idx)
    move(4, idx)

    errors = []

    for i in range(4):
        pos, result, error = servo.ReadPos(i+1)
        errors.append(error)
        
    print(f"Servo Error: {errors}")

    time.sleep(2)
finally:
    port.closePort()
