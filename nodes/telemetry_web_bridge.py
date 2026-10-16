#!/usr/bin/env python3
"""
ROS 2 Basic Telemetry Web Bridge Node for Trash Sorting Robot
Reads 100% actual physical Odometry pose feedback (posX, posY) from Gazebo Sim 3D
and streams basic pose data to Web Monitoring at http://localhost:8080/api/telemetry.

NO PATH PLANNING, NO WAYPOINTS, NO CP TARGET CALCULATIONS.
"""

import sys
import time
import math
import json
import urllib.request
import urllib.error

# ROS 2 Integration
HAS_RCLPY = False
try:
    import rclpy
    from rclpy.node import Node
    from nav_msgs.msg import Odometry
    from geometry_msgs.msg import Twist
    HAS_RCLPY = True
except ImportError:
    HAS_RCLPY = False

TELEMETRY_URL = "http://localhost:8080/api/telemetry"
CMD_VEL_URL = "http://localhost:8080/api/cmd_vel"
POST_INTERVAL = 0.1  # 10 Hz update rate

class TelemetryWebBridgeNode(Node if HAS_RCLPY else object):
    def __init__(self):
        if HAS_RCLPY:
            super().__init__('telemetry_web_bridge_node')
            
            # Subscriptions & Publishers
            self.odom_sub = self.create_subscription(
                Odometry,
                '/model/trash_bot/odometry',
                self.odom_callback,
                10
            )
            self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
            self.cmd_pub_alt = self.create_publisher(Twist, '/model/trash_bot/cmd_vel', 10)

        # Pose Defaults & State
        self.curr_x = 9.5
        self.curr_y = 0.6
        self.heading = math.pi
        self.battery_pct = 95.0
        self.battery_voltage = 12.4
        self.start_time = time.time()
        self.last_cmd_timestamp = 0

    def poll_web_cmd_vel(self):
        """Membaca sinyal perintah gerak teleop dari Web Dashboard & mengirimkan ke Gazebo /cmd_vel"""
        try:
            req = urllib.request.Request(CMD_VEL_URL, method='GET')
            with urllib.request.urlopen(req, timeout=0.2) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                ts = data.get("timestamp", 0)
                if ts > self.last_cmd_timestamp and (time.time() - ts) < 1.0:
                    self.last_cmd_timestamp = ts
                    lx = float(data.get("linearX", 0.0))
                    az = float(data.get("angularZ", 0.0))
                    if HAS_RCLPY and hasattr(self, 'cmd_pub'):
                        msg = Twist()
                        msg.linear.x = lx
                        msg.angular.z = az
                        self.cmd_pub.publish(msg)
                        self.cmd_pub_alt.publish(msg)
        except Exception:
            pass

    def odom_callback(self, msg):
        """Callback Odometri Gazebo Real-Time (Transformasi Odometri Lokal ke Arena World)"""
        px = msg.pose.pose.position.x
        py = msg.pose.pose.position.y
        
        # Transformasi Odometri Lokal DiffDrive (0,0 saat spawn) ke Koordinat Arena (START: 9.50, 0.60)
        self.curr_x = 9.50 - px
        self.curr_y = 0.60 - py
        
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.heading = math.atan2(siny_cosp, cosy_cosp)

    def post_telemetry(self):
        # Battery Simulation
        elapsed = time.time() - self.start_time
        self.battery_pct = max(15.0, 95.0 - (elapsed / 300.0) * 5.0)
        self.battery_voltage = 10.0 + (self.battery_pct / 100.0) * 2.6

        payload = {
            "connected": True,
            "cameraConnected": True,
            "operationState": "Ready",
            "posX": round(self.curr_x, 2),
            "posY": round(self.curr_y, 2),
            "currentCP": "START",
            "nextCP": "-",
            "distanceToNext": 0.0,
            "etaSeconds": 0,
            "batteryVoltage": round(self.battery_voltage, 1),
            "batteryPct": int(self.battery_pct)
        }

        req = urllib.request.Request(
            TELEMETRY_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=0.5) as resp:
                pass
        except Exception:
            pass

def main():
    print("=" * 65)
    print("📡 ROS 2 BASIC TELEMETRY WEB BRIDGE NODE")
    print(f"🌐 Target Endpoint: {TELEMETRY_URL}")
    print("📡 Topic: /model/trash_bot/odometry")
    print("=" * 65)

    if not HAS_RCLPY:
        print("❌ Error: rclpy not installed or ROS 2 environment not sourced.")
        sys.exit(1)

    rclpy.init()
    node = TelemetryWebBridgeNode()

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.05)
            node.poll_web_cmd_vel()
            node.post_telemetry()
            time.sleep(POST_INTERVAL)
    except KeyboardInterrupt:
        print("\n🛑 Telemetry Web Bridge Node stopped by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
