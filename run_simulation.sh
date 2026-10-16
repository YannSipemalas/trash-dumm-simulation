#!/usr/bin/env bash
# ==============================================================================
# Trash Sorting Robot Basic Gazebo Simulation Launcher
# Pure World & Model Simulation - ZERO PATH PLANNING
# ==============================================================================

SIM_DIR="/home/yanzz/Documents/SIMULASI TRASH-DUMM"
WORLD_PATH="$SIM_DIR/worlds/trash_arena.sdf"
MODEL_PATH="$SIM_DIR/models"
TELEMETRY_NODE="$SIM_DIR/nodes/telemetry_web_bridge.py"

echo "============================================================"
echo "🚀 LAUNCHING BASIC GAZEBO SIMULATION & POSE TELEMETRY BRIDGE"
echo "============================================================"
echo "📂 Simulation Path: $SIM_DIR"
echo "🌍 World File:      $WORLD_PATH"
echo "📡 Telemetry Node:  $TELEMETRY_NODE"
echo "============================================================"

# Set Gazebo Resource Path so model trash_bot is recognized
export GZ_SIM_RESOURCE_PATH="$MODEL_PATH:$GZ_SIM_RESOURCE_PATH"
export IGN_GAZEBO_RESOURCE_PATH="$MODEL_PATH:$IGN_GAZEBO_RESOURCE_PATH"

# Function to handle shutdown on Ctrl+C
cleanup() {
    echo -e "\n🛑 Shutting down Gazebo Simulation and Telemetry Bridge..."
    pkill -f "telemetry_web_bridge.py" 2>/dev/null
    pkill -f "parameter_bridge" 2>/dev/null
    pkill -f "gz sim" 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# 1. Source ROS 2 environment
if [ -f "/opt/ros/jazzy/setup.bash" ]; then
    source /opt/ros/jazzy/setup.bash
elif [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi

# 2. Launch ROS 2 - Gazebo Sim Parameter Bridge (/cmd_vel & /odometry)
echo "▶️ Starting ROS 2 <-> Gazebo Sim Parameter Bridge..."
ros2 run ros_gz_bridge parameter_bridge \
    /cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist \
    /model/trash_bot/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist \
    /model/trash_bot/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry >/dev/null 2>&1 &
BRIDGE_ROS_PID=$!

sleep 1

# 3. Start Basic Telemetry Web Bridge Node (Pure Pose Streaming)
echo "▶️ Starting Basic Telemetry Web Bridge Node..."
python3 "$TELEMETRY_NODE" &
TELEMETRY_PID=$!

sleep 1

# 4. Launch Gazebo Sim 3D World (Unpaused Physics with -r)
if command -v gz &> /dev/null; then
    echo "▶️ Launching Gazebo Sim (gz sim -r)..."
    gz sim -r "$WORLD_PATH"
elif command -v ign &> /dev/null; then
    echo "▶️ Launching Ignition Gazebo (ign gazebo -r)..."
    ign gazebo -r "$WORLD_PATH"
else
    echo "⚠️ Gazebo GUI not found in PATH. Running Telemetry Node..."
    wait $TELEMETRY_PID
fi

cleanup
