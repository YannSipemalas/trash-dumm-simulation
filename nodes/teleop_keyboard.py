#!/usr/bin/env python3
"""
ROS 2 Teleop Keyboard Controller Node for 4-Mecanum Wheel Trash Sorting Robot
Allows manual driving control using WASD & QE keys in the terminal.

Controls:
    [W] : Move Forward      (+0.5 m/s)
    [S] : Move Backward     (-0.5 m/s)
    [Q] : Strafe Left       (+0.5 m/s)
    [E] : Strafe Right      (-0.5 m/s)
    [A] : Turn Left         (+0.8 rad/s)
    [D] : Turn Right        (-0.8 rad/s)
    [SPACE] / [X] : STOP (0 m/s, 0 rad/s)
    [Ctrl+C]      : Quit
"""

import sys
import select
import termios
import tty
import time

HAS_RCLPY = False
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    HAS_RCLPY = True
except ImportError:
    HAS_RCLPY = False

LINEAR_SPEED = 0.5   # m/s
ANGULAR_SPEED = 0.8  # rad/s

HELP_MSG = """
============================================================
🎮 ROS 2 KEYBOARD TELEOP (4-MECANUM WHEEL OMNIDIRECTIONAL)
============================================================
  W : Move Forward     (+0.5 m/s)
  S : Move Backward    (-0.5 m/s)
  Q : Strafe Left      (+0.5 m/s)
  E : Strafe Right     (-0.5 m/s)
  A : Turn Left        (+0.8 rad/s)
  D : Turn Right       (-0.8 rad/s)
  SPACE / X : STOP

  Press Ctrl+C to Quit
============================================================
"""

def get_key(settings):
    """Membaca 1 karakter keyboard dari terminal tanpa tombol Enter."""
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main():
    if not HAS_RCLPY:
        print("❌ Error: rclpy tidak terinstall atau lingkungan ROS 2 belum di-source.")
        sys.exit(1)

    print(HELP_MSG)
    settings = termios.tcgetattr(sys.stdin)

    rclpy.init()
    node = Node('teleop_keyboard_node')
    cmd_pub = node.create_publisher(Twist, '/cmd_vel', 10)
    cmd_pub_alt = node.create_publisher(Twist, '/model/trash_bot/cmd_vel', 10)

    linear_x = 0.0
    linear_y = 0.0
    angular_z = 0.0
    status_text = "STOPPED"

    try:
        while rclpy.ok():
            key = get_key(settings)
            
            if key in ['w', 'W']:
                linear_x = LINEAR_SPEED
                linear_y = 0.0
                angular_z = 0.0
                status_text = "FORWARD"
            elif key in ['s', 'S']:
                linear_x = -LINEAR_SPEED
                linear_y = 0.0
                angular_z = 0.0
                status_text = "BACKWARD"
            elif key in ['q', 'Q']:
                linear_x = 0.0
                linear_y = LINEAR_SPEED
                angular_z = 0.0
                status_text = "STRAFE LEFT"
            elif key in ['e', 'E']:
                linear_x = 0.0
                linear_y = -LINEAR_SPEED
                angular_z = 0.0
                status_text = "STRAFE RIGHT"
            elif key in ['a', 'A']:
                linear_x = 0.0
                linear_y = 0.0
                angular_z = ANGULAR_SPEED
                status_text = "TURN LEFT"
            elif key in ['d', 'D']:
                linear_x = 0.0
                linear_y = 0.0
                angular_z = -ANGULAR_SPEED
                status_text = "TURN RIGHT"
            elif key in [' ', 'x', 'X', 'k', 'K']:
                linear_x = 0.0
                linear_y = 0.0
                angular_z = 0.0
                status_text = "STOPPED"
            elif key in ['\x03']: # Ctrl+C
                print("\n🛑 Shutting down Keyboard Teleop...")
                break

            # Publish velocity command
            twist = Twist()
            twist.linear.x = float(linear_x)
            twist.linear.y = float(linear_y)
            twist.angular.z = float(angular_z)
            cmd_pub.publish(twist)
            cmd_pub_alt.publish(twist)

            if key:
                print(f"\r🎮 Command Sent: [{key.upper()}] -> Status: {status_text:14s} (Lx: {linear_x:+.1f}, Ly: {linear_y:+.1f}, Az: {angular_z:+.1f})", end="", flush=True)

            time.sleep(0.05)

    except Exception as e:
        print(f"\n⚠️ Error: {e}")
    finally:
        # Send zero velocity on exit
        twist = Twist()
        cmd_pub.publish(twist)
        cmd_pub_alt.publish(twist)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()
        print("\n👋 Teleop Keyboard Node terminated gracefully.")

if __name__ == '__main__':
    main()
