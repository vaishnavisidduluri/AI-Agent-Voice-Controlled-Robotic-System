import math

class IKSolver:
    def __init__(self):
        self.l1 = 10
        self.l2 = 10
        self.l3 = 10

    def solve(self, x, y, z):
        try:
            theta1 = math.degrees(math.atan2(y, x))

            r = math.sqrt(x**2 + y**2)
            z_offset = z - self.l1

            d = math.sqrt(r**2 + z_offset**2)

            if d > (self.l2 + self.l3):
                print("⚠️ Target out of reach")
                d = self.l2 + self.l3 - 1

            cos_theta3 = (d**2 - self.l2**2 - self.l3**2) / (2 * self.l2 * self.l3)
            theta3 = math.degrees(math.acos(max(-1, min(1, cos_theta3))))

            cos_theta2 = (d**2 + self.l2**2 - self.l3**2) / (2 * self.l2 * d)
            theta2 = math.degrees(math.acos(max(-1, min(1, cos_theta2))))

            theta2 = theta2 + math.degrees(math.atan2(z_offset, r))

            return {
                "servo1": int(theta1),
                "servo2": int(theta2),
                "servo3": int(theta3)
            }

        except Exception as e:
            print("❌ IK Error:", e)
            return None