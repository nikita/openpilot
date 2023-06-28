#!/usr/bin/env python3
import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from panda import Panda  # noqa: E402
from selfdrive.car import make_can_msg
from selfdrive.car.toyota.values import CAR, STATIC_DSU_MSGS

# This is the white panda serial that im using
PANDA_SERIAL = "0d801b000f51363038363036"
CAR_FINGERPRINT = CAR.COROLLA
ENABLE_DSU = True
# Combined both TSS2 Radar CANBUSES into white panda CAN0
RADAR_CANBUS_ID = 0

# 100hz
cycletime = 0.01  # seconds

if __name__ == "__main__":
  serials = Panda.list()
  print(f"found {len(serials)} panda(s) - {serials}")

  p = Panda(serial=PANDA_SERIAL)
  p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)
  p.set_power_save(False)

  frame = 0

  while True:
    start = time.monotonic()

    can_sends = []

    for addr, cars, bus, fr_step, data in STATIC_DSU_MSGS:
      if frame % fr_step == 0 and ENABLE_DSU and CAR_FINGERPRINT in cars:
        can_sends.append(make_can_msg(addr, data, RADAR_CANBUS_ID))

    p.can_send_many(can_sends)
    print("Sent", frame)

    if frame == 100:
      frame = 0
    else:
      frame += 1

    delta = time.monotonic() - start
    if delta < cycletime:  # Did we finish in time?
      time.sleep(cycletime - delta)  # Sleep the rest of the time.
    else:
      print('WARNING: cycle too long!')
    