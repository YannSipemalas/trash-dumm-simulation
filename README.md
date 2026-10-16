# 🤖 Gazebo Simulation & Real-Time Telemetry Bridge - Trash Sorting Robot

Dokumentasi resmi untuk desain simulasi 3D Gazebo dan modul **Telemetry Bridge** pergerakan robot pemilah sampah (*Trash Sorting Robot*).

Folder Simulasi: `/home/yanzz/Documents/SIMULASI TRASH-DUMM`

---

## 📌 1. Tujuan Simulasi

Simulasi Gazebo ini dibuat untuk **mensinkronkan pergerakan robot virtual dengan Web Monitoring** sebelum robot fisik (*hardware*) selesai dibuat:
1. Menyediakan dunia virtual 3D (*Gazebo World*) dengan denah arena yang presisi sesuai blueprint arena (terdiri dari 4 Meja, 2 Lapangan Bola, area START, FINISH, dan Checkpoints CP1–CP4).
2. Menjalankan sistem kontrol pergerakan navigasi robot secara terus-menerus (*looping*).
3. Mengirimkan data telemetri real-time (posisi $X, Y$, checkpoint target, sisa jarak, ETA, dan baterai) ke backend **Web Monitoring** (`http://localhost:8080/api/telemetry`).

---

## 🔄 2. Alur Pergerakan Waypoint (Continuous Looping)

Robot ditempatkan di **Area Start**, kemudian bergerak otomatis mengikuti urutan checkpoint:

$$\text{START} \longrightarrow \text{CP 1} \longrightarrow \text{CP 2} \longrightarrow \text{CP 3} \longrightarrow \text{CP 4} \longrightarrow \text{CP 1} \longrightarrow \text{CP 2} \dots$$

```
              GAZEBO (Virtual Robot)
                         │
                         ▼
                      START
                         │
                         ▼
                       CP 1
                         │
                         ▼
                       CP 2
                         │
                         ▼
                       CP 3
                         │
                         ▼
                       CP 4
                         │
                         └──────────────┐
                                        │
                                        ▼
                                      CP 1
                                        │
                                 🔄 LOOPING
                                        │
                                        ▼
                               CP 2 → CP 3 → CP 4
```

---

## 🌐 3. Mekanisme Penarikan Data oleh Web Monitoring

1. **Pengambilan Posisi Gazebo**: Script `scripts/gazebo_telemetry_bridge.py` membaca koordinat presisi $(x, y)$ dan sudut orientasi $\theta$ robot di dalam simulasi Gazebo.
2. **Pengiriman HTTP POST**: Script mengirimkan payload JSON telemetri ke server web setiap 200 ms:
   ```json
   {
     "connected": true,
     "cameraConnected": true,
     "operationState": "PATROLLING",
     "posX": 2.45,
     "posY": 3.12,
     "currentCP": "CP1",
     "nextCP": "CP2",
     "distanceToNext": 3.8,
     "etaSeconds": 7,
     "batteryVoltage": 12.4,
     "batteryPct": 95
   }
   ```
3. **Rendering Dashboard Web**: Server `server.py` menanti data telemetri dan memperbarui state global. Web Frontend (`js/app.js` & `js/arena.js`) menarik data tersebut dan menggerakkan ikon robot pada canvas denah secara real-time.

---

## 📁 4. Struktur Folder Project

```
/home/yanzz/Documents/SIMULASI TRASH-DUMM/
├── models/
│   └── trash_bot/
│       ├── model.config         # Konfigurasi model Gazebo
│       └── model.sdf            # Model SDF 3D Robot Differential Drive
├── worlds/
│   └── trash_arena.sdf          # World Gazebo (4 Meja, 2 Lapangan, CP1-CP4, Start, Finish)
├── scripts/
│   └── gazebo_telemetry_bridge.py # Controller Navigasi Waypoint & Telemetry POST Bridge
├── run_simulation.sh            # Script Shell untuk menjalankan Simulasi + Bridge
└── README.md                    # Dokumentasi lengkap
```

---

## 🚀 5. Cara Menjalankan Simulasi

### Step 1: Pastikan Web Monitoring Server Aktif
Buka terminal dan jalankan server backend web monitoring di port 8080:
```bash
cd "/home/yanzz/Documents/WEB MONITORING TRASHBOT"
python3 server.py
```

### Step 2: Menjalankan Simulasi Gazebo & Telemetry Bridge
Buka terminal baru dan jalankan script utama:
```bash
cd "/home/yanzz/Documents/SIMULASI TRASH-DUMM"
./run_simulation.sh
```

### Step 3: Buka Web Monitoring
Akses browser ke `http://localhost:8080`. Ikon robot pada peta arena 2D akan bergerak secara otomatis dan sinkron sesuai dengan posisi robot simulasi Gazebo!
