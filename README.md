# 🧹🤖 Süpürge Robotu – Oda Bazlı Temizlik ve QR Doğrulama
**ROS1 Noetic | TurtleBot3 | Gazebo**

---

## 📌 Proje Tanımı
Bu proje, Gazebo simülasyon ortamında çalışan bir **TurtleBot3 süpürge robotunun**
ev ortamında **otonom, oda bazlı temizlik** yapmasını amaçlamaktadır.

Robot;
- 🗺️ Evin haritasını çıkarır ve kaydeder  
- 📍 Kaydedilen harita üzerinde kendini konumlandırır (AMCL)  
- 🚪 Önceden tanımlı odalara sırayla gider  
- 📷 Oda girişlerinde QR kod okuyarak doğrulama yapar  
- ✅ Doğru odadaysa temizlik rotasını tamamlar  
- 📝 Sürecin sonunda temizlik raporu üretir  

Simülasyon ortamı olarak **turtlebot3_house** kullanılmıştır.

---

## ⚙️ Kullanılan Teknolojiler
- ROS1 Noetic
- Gazebo
- TurtleBot3 (waffle / waffle_pi)
- SLAM (gmapping)
- Navigation Stack (AMCL + move_base)
- OpenCV
- pyzbar (QR kod çözümleme)
- YAML tabanlı görev tanımı

---

## 🎬 Senaryo Akışı
1. Gazebo ortamı başlatılır  
2. SLAM ile evin haritası çıkarılır ve kaydedilir  
3. Kaydedilen harita ile AMCL üzerinden lokalizasyon yapılır  
4. Görev yöneticisi sırayla odalara hedef gönderir  
5. Oda girişinde QR kod okunur  
6. QR doğrulaması başarılıysa:
   - 🧹 Odaya ait 3–5 waypoint’lik temizlik rotası tamamlanır  
7. QR doğrulaması başarısızsa:
   - ⏭️ Oda atlanır  
8. Tüm odalar tamamlandığında:
   - 📊 Temizlik raporu oluşturulur  

---

## 🏠 Temizlenen Odalar
Projede aşağıdaki odalar bulunmaktadır:
- 🛋️ LIVINGROOM
- 🍳 KITCHEN
- 🛏️ BEDROOM
- 🚽 TOILET

Her oda için:
- 1 adet giriş waypoint’i  
- 3–5 adet temizlik waypoint’i  
- 1 adet QR kod  

---

## 📁 Proje Klasör Yapısı
odev/
├── launch/
│ ├── gazebo.launch
│ ├── amcl.launch
│ ├── move_base.launch
│
├── worlds/
│ └── ev_dunyasi.world
│
├── maps/
│ ├── ev_haritam.yaml
│ └── ev_haritam.pgm
│
├── config/
│ └── mission.yaml
│
├── src/
│ └── mission_manager.py
│
├── qr_codes/
│ ├── livingroom_qr.png
│ ├── kitchen_qr.png
│ ├── bedroom_qr.png
│ └── toilet_qr.png
│
└── README.md


---

## 🧾 mission.yaml
Görevler ve waypoint’ler **config/mission.yaml** dosyasından okunmaktadır.

Bu dosyada:
- 🏠 Oda sırası  
- 📍 Oda giriş hedefleri  
- 🧹 Temizlik waypoint’leri  
- 🔳 Beklenen QR içerikleri  

tanımlıdır.  
Bu sayede görev senaryosu **kodu değiştirmeden** düzenlenebilir.

---

## ⚠️ Hata Yönetimi
- QR okunamazsa:
  - 2 kez tekrar denenir
  - Başarısızsa oda **SKIPPED**
- move_base hedefe ulaşamazsa:
  - 1 kez tekrar denenir
  - Yine başarısızsa **FAIL**
- Her oda için timeout mekanizması uygulanır

---

## 🛠️ Kurulum
```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash

---

▶️ Çalıştırma Adımları

🖥️Terminal 1 – Gazebo 
source ~/catkin_ws/devel/setup.bash
export GAZEBO_RESOURCE_PATH=$GAZEBO_RESOURCE_PATH:~/catkin_ws/src/odev
roslaunch odev gazebo.launch

🧭 Terminal 2 – Navigation
source ~/catkin_ws/devel/setup.bash
roslaunch turtlebot3_navigation turtlebot3_navigation.launch \
map_file:=/home/ubuntu/catkin_ws/src/odev/maps/ev_haritam.yaml

🧠 Terminal 3 – Görev Yöneticisi
source ~/catkin_ws/devel/setup.bash
rosrun odev mission_manager.py

---

📊 Üretilen Çıktılar
   - Gazebo ortamında çalışan robot
   - SLAM ile oluşturulmuş harita
   - AMCL ile başarılı lokalizasyon
   - Oda bazlı navigasyon
   - QR doğrulama sistemi
   - Oda içi mini temizlik turları
   - cleaning_report.txt raporu

---


👩‍💻 Geliştirici
Kader Kaya
Yazılım Mühendisliği Öğrencisi
ROS & Robotik Sistemler 🚀
