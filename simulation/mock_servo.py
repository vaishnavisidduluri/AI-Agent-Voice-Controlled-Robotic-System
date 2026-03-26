class MockServo:

    def move(self, servo_id, angle):
        print(f"[SIM] Moving Servo {servo_id} → {angle}°")

    def control_gripper(self, action):
        print(f"[SIM] Gripper → {action}")