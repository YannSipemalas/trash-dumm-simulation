# Trash-Dumm Gazebo Simulation — Trash Sorting Robot

Simulasi 3D Gazebo dan **Telemetry Web Bridge** untuk robot pemilah sampah (*Trash Sorting Robot*).

> [!NOTE]
> **Status saat ini: MODE MANUAL (Teleop).**
> Robot digerakkan secara manual menggunakan keyboard atau tombol di Web Dashboard.
> Navigasi autonomous (waypoint / path planning) **belum diimplementasikan** — lihat bagian [Rencana Pengembangan](#7-rencana-pengembangan).

![Desain World Gazebo](Desain%20World.png)

---

## 1. Tujuan Simulasi

Simulasi ini dibuat untuk **menyinkronkan pergerakan robot virtual dengan Web Monitoring** sebelum robot fisik selesai dibuat:

1. Menyediakan dunia virtual 3D (*Gazebo World*) sesuai blueprint arena: 4 Meja, 2 Lapangan Bola, area START, FINISH, dan Checkpoint CP1–CP4.
2. Menggerakkan robot secara **manual** melalui teleop (keyboard terminal atau Web Dashboard).
3. Mengirim posisi robot (X, Y) dan data simulasi baterai secara real-time ke backend Web Monitoring (`http://localhost:8080/api/telemetry`).

---

## 2. Alur Sistem (Mode Manual)

```
 ┌──────────────────────────┐      ┌──────────────────────────┐
 │ Teleop Keyboard (Terminal)│      │ Tombol Teleop Web Dashboard│
 │  nodes/teleop_keyboard.py │      │   → POST /api/cmd_vel     │
 └────────────┬─────────────┘      └────────────┬─────────────┘
              │ publish Twist                    │ GET /api/cmd_vel
              │                                  ▼
              │                    nodes/telemetry_web_bridge.py
              │                                  │ publish Twist
              ▼                                  ▼
        ROS 2 topic  /cmd_vel  &  /model/trash_bot/cmd_vel
                              │
                              ▼  (ros_gz_bridge)
                  Gazebo Sim — robot trash_bot bergerak
                              │
                              ▼  /model/trash_bot/odometry
               nodes/telemetry_web_bridge.py
                              │  POST /api/telemetry (10 Hz)
                              ▼
               Web Monitoring — ikon robot bergerak di peta arena
```

---

## 3. Kontrol Teleop Keyboard

| Tombol | Aksi | Kecepatan |
|---|---|---|
| `W` | Maju | +0.5 m/s |
| `S` | Mundur | -0.5 m/s |
| `Q` | Geser kiri (strafe) | +0.5 m/s |
| `E` | Geser kanan (strafe) | -0.5 m/s |
| `A` | Putar kiri | +0.8 rad/s |
| `D` | Putar kanan | -0.8 rad/s |
| `SPACE` / `X` / `K` | STOP | 0 |
| `Ctrl+C` | Keluar | — |

---

## 4. Data Telemetri ke Web Monitoring

`telemetry_web_bridge.py` membaca odometri Gazebo, mengubahnya ke koordinat arena (titik START = `9.50, 0.60`), lalu mengirim JSON berikut setiap **100 ms (10 Hz)**:

```json
{
  "connected": true,
  "cameraConnected": true,
  "operationState": "Ready",
  "posX": 9.50,
  "posY": 0.60,
  "currentCP": "START",
  "nextCP": "-",
  "distanceToNext": 0.0,
  "etaSeconds": 0,
  "batteryVoltage": 12.5,
  "batteryPct": 95
}
```

| Field | Keterangan |
|---|---|
| `posX`, `posY` | ✅ Posisi nyata dari odometri Gazebo |
| `batteryVoltage`, `batteryPct` | ⚠️ Simulasi (turun perlahan seiring waktu) |
| `currentCP`, `nextCP`, `distanceToNext`, `etaSeconds` | ⚠️ Nilai tetap — belum dihitung karena belum ada navigasi autonomous |

---

## 5. Struktur Folder

```
SIMULASI TRASH-DUMM/
├── models/
│   └── trash_bot/
│       ├── meshes/                  # Mesh 3D robot
│       ├── model.config             # Konfigurasi model Gazebo
│       └── model.sdf                # Model SDF robot
├── worlds/
│   └── trash_arena.sdf              # World arena (4 Meja, 2 Lapangan, CP1–CP4, Start, Finish)
├── nodes/
│   ├── telemetry_web_bridge.py      # Bridge: odometri → Web, cmd_vel Web → ROS 2
│   └── teleop_keyboard.py           # Kontrol manual via keyboard (WASD + QE)
├── run_simulation.sh                # Menjalankan Gazebo + ros_gz_bridge + telemetry bridge
└── README.md
```

---

## 6. Cara Menjalankan

**Kebutuhan:** Ubuntu 24.04, ROS 2 Jazzy (atau Humble), Gazebo Sim (`gz`), paket `ros_gz_bridge`.

### Step 1 — (Opsional) Jalankan Web Monitoring Server
```bash
cd "/home/yanzz/Documents/WEB MONITORING TRASHBOT"
python3 server.py
```

### Step 2 — Jalankan Simulasi Gazebo
```bash
cd "/home/yanzz/Documents/SIMULASI TRASH-DUMM"
./run_simulation.sh
```

### Step 3 — Gerakkan Robot dengan Keyboard (terminal baru)
```bash
source /opt/ros/jazzy/setup.bash
cd "/home/yanzz/Documents/SIMULASI TRASH-DUMM"
python3 nodes/teleop_keyboard.py
```

### Step 4 — Buka Web Monitoring
Akses `http://localhost:8080`. Ikon robot di peta arena bergerak sesuai posisi robot di Gazebo. Robot juga bisa digerakkan dari tombol teleop di dashboard.

Tekan **Ctrl+C** di terminal simulasi untuk menghentikan semua proses.

---

## 7. Rencana Pengembangan

- [ ] Navigasi autonomous mengikuti waypoint: `START → CP1 → CP2 → CP3 → CP4 → (looping)`
- [ ] Perhitungan `currentCP`, `nextCP`, `distanceToNext`, dan `etaSeconds` secara real-time
- [ ] Integrasi kamera / AI vision untuk deteksi sampah
- [ ] Path `SIM_DIR` di `run_simulation.sh` dibuat relatif agar bisa dijalankan di komputer lain
