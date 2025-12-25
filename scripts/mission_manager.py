#!/usr/bin/env python3
import rospy
import yaml
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from pyzbar import pyzbar
import tf.transformations

class CleaningManager:
    def __init__(self):
        rospy.init_node('mission_manager_node')
        
        # 1. YAML Dosyasını Yükleme 
        yaml_path = "/home/ubuntu/catkin_ws/src/odev/config/mission.yaml"
        # Rapor dosyası yolu
        self.report_path = "/home/ubuntu/catkin_ws/src/odev/cleaning_report.txt"
        
        with open(yaml_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.bridge = CvBridge()
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        self.client.wait_for_server()
        
        self.current_qr = None
        self.results = {} # Rapor için sonuçları tutacak
        
        # Kamera topic'ini dinle
        rospy.Subscriber("/camera/rgb/image_raw", Image, self.image_callback)
        
        rospy.loginfo("Sistem Hazır! Görev Başlıyor...")

    def image_callback(self, msg):
        cv_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        decoded_objects = pyzbar.decode(cv_img)
        if decoded_objects:
            self.current_qr = decoded_objects[0].data.decode("utf-8")
        else:
            self.current_qr = None 

    def go_to(self, x, y, yaw, timeout=90):
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y
        
        q = tf.transformations.quaternion_from_euler(0, 0, yaw)
        goal.target_pose.pose.orientation.x = q[0]
        goal.target_pose.pose.orientation.y = q[1]
        goal.target_pose.pose.orientation.z = q[2]
        goal.target_pose.pose.orientation.w = q[3]
        
        self.client.send_goal(goal)
        finished = self.client.wait_for_result(rospy.Duration(timeout))
        
        if not finished:
            self.client.cancel_goal()
            return False
            
        return self.client.get_state() == actionlib.GoalStatus.SUCCEEDED

    def save_report(self):
        with open(self.report_path, "w") as f:
            f.write("--- TEMİZLİK RAPORU ---\n")
            for room, status in self.results.items():
                f.write(f"{room}: {status}\n")

    def run(self):
        for room_name in self.config['rooms']:
            room = self.config[room_name]
            rospy.loginfo(f"--- {room_name} Odasına Gidiliyor ---")
            
            # ADIM 1: Kapıya Git
            success = self.go_to(room['entry_goal']['x'], room['entry_goal']['y'], room['entry_goal']['yaw'])
            if not success:
                # MESAJ BURAYA EKLENDİ
                rospy.logwarn(f"DIKKAT: {room_name} kapisina ulasilamadi (Sure doldu). Tekrar deneniyor...")
                success = self.go_to(room['entry_goal']['x'], room['entry_goal']['y'], room['entry_goal']['yaw'])

            if not success:
                rospy.logerr(f"HATA: {room_name} kapisina ulasim tamamiyle basarisiz. Bu oda atlaniyor!")
                self.results[room_name] = "FAIL (Ulaşım Hatası)"
                continue
            
            # ADIM 2: QR Oku ve Doğrula
            rospy.loginfo("Kapıya varıldı, QR taranıyor...")
            verified = False
            for attempt in range(1, 3): 
                if attempt > 1:
                    rospy.loginfo("QR tekrar taranıyor (Deneme 2)...")
                    self.go_to(room['entry_goal']['x']+0.05, room['entry_goal']['y'], 3.14, timeout=15)
                
                rospy.sleep(3) 
                if self.current_qr == room['qr_expected']:
                    verified = True
                    break

            if verified:
                rospy.loginfo(f"DOĞRULAMA BAŞARILI: {self.current_qr}")
                
                # ADIM 3: Temizlik Noktalarını Gez
                clean_count = 0
                for i, p in enumerate(room['cleaning_goals']):
                    rospy.loginfo(f"{room_name} temizleniyor... {i+1}. Nokta ")
                    if self.go_to(p['x'], p['y'], p['yaw'], timeout=45):
                        clean_count += 1
                    else:
                        # MESAJ BURAYA EKLENDİ
                        rospy.logwarn(f"UYARI: {i+1}. Nokta icin sure doldu. Siradaki noktaya geciliyor...")
                
                rospy.loginfo(f"{room_name} TAMAMLANDI.")
                self.results[room_name] = f"SUCCESS ({clean_count} nokta)"
            else:
                rospy.logerr(f"HATA! Beklenen: {room['qr_expected']}, Okunan: {self.current_qr}")
                rospy.loginfo(f"{room_name} QR kodu doğrulanamadığı için atlanıyor...")
                self.results[room_name] = "SKIPPED (QR Hatası)"

        rospy.loginfo("TÜM ODALARA BAKILDI VE TEMİZLİK BİTTİ!")
        self.save_report() 

if __name__ == '__main__':
    try:
        manager = CleaningManager()
        manager.run()
    except rospy.ROSInterruptException:
        pass
