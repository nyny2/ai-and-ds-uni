# Projet "robotique" IA&Jeux 2025
# Binome:
# Prénom Nom No_étudiant/e : Lara Camogozoglu 21301085
# Prénom Nom No_étudiant/e : Eda Girgin 21313187

from robot import *
import math
import random

nb_robots = 0

class Robot_player(Robot):
    
    # TAKIM ADI
    team_name = "EdaLara" 
    
    robot_id = -1
    
    # TEK HAFIZA KURALI (Integer)
    # 0-50 arası: Başlangıç dağılması (Initialization)
    # 51-100: Normal mod ve Sıkışma sayacı
    memory = 0 

    # GA AĞIRLIKLARI (Genetik Algoritma sonucu elde edilmiş agresif değerler)
    # Hızlanma odaklı: Ön sensörlerin ağırlığı çok yüksek
    GENOME_SPEED = [1.0, 0.0, 1.0, 0.0] 
    # Dönüş odaklı: Yan sensörler ters etki yapar
    GENOME_ROT = [0.0, 2.0, 0.0, -2.0]

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        
        # Sensörleri oku
        s_left = sensors[sensor_front_left]
        s_front = sensors[sensor_front]
        s_right = sensors[sensor_front_right]
        
        # --- KATMAN 3 (EN ÜST): BAŞLANGIÇ DAĞILMASI (Start-Burst) ---
        # Oyunun başında robotlar birbirine çarpıp vakit kaybetmesin diye
        # memory 0'dan 20'ye kadar zorla dağıtıyoruz.
        if self.memory < 20:
            self.memory += 1
            translation = 1.0 # Tam gaz ileri
            
            # Robot ID'sine göre farklı yönlere zorla
            # Robot 0: Sola sert, Robot 1: Sağa sert, Robot 2: Hafif Sol, Robot 3: Hafif Sağ
            if self.robot_id % 4 == 0: rotation = 0.5
            elif self.robot_id % 4 == 1: rotation = -0.5
            elif self.robot_id % 4 == 2: rotation = 0.2
            else: rotation = -0.2
            
            return translation, rotation, False

        # --- KATMAN 2: SIKIŞMA KURTARMA (Stuck Recovery) ---
        # Eğer önümüz çok kapalıysa memory sayacını (50'den başlayarak) artır
        if s_front < 0.15 or (s_left < 0.15 and s_right < 0.15):
            self.memory += 1
        else:
            # Sıkışık değilsek sayacı 20'ye (normal moda) geri çek
            if self.memory > 20:
                self.memory = 20

        # Eğer sayaç 40'ı geçerse (yani 20 adımdır sıkışıksak)
        if self.memory > 40:
            # KURTULMA MANEVRASI
            translation = -1.0 # Tam gaz geri
            rotation = 1.0 if self.robot_id % 2 == 0 else -1.0 # Olduğun yerde dön
            
            # 60'a gelince sıfırla ki döngüye girmesin
            if self.memory > 60:
                self.memory = 20
            return translation, rotation, False

        # --- KATMAN 1: ACİL DUVAR REFLEKSİ (Smart Braitenberg) ---
        # Duvara toslamadan hemen önce çok sert dön
        if s_front < 0.4:
            translation = 0.0 # Çarpmamak için anlık duraksama
            # Hangi taraf daha boşsa ORAYA dön (klasik Braitenberg'in tersi, boşluğa kaçış)
            if s_left > s_right:
                rotation = 0.8 # Sola dön
            else:
                rotation = -0.8 # Sağa dön
            return translation, rotation, False

        # --- KATMAN 0: GA OPTİMİZASYONLU "HIZLI GEZİNTİ" ---
        # Hedef: Maksimum hızla git, sadece gerekirse hafif dön.
        
        # V = w0 + w1*L + w2*F + w3*R
        raw_trans = self.GENOME_SPEED[0] + \
                    self.GENOME_SPEED[1]*s_left + \
                    self.GENOME_SPEED[2]*s_front + \
                    self.GENOME_SPEED[3]*s_right
        
        # R = w0 + w1*L + w2*F + w3*R
        raw_rot = self.GENOME_ROT[0] + \
                  self.GENOME_ROT[1]*s_left + \
                  self.GENOME_ROT[2]*s_front + \
                  self.GENOME_ROT[3]*s_right

        translation = math.tanh(raw_trans)
        rotation = math.tanh(raw_rot)

        # AGRESİF HIZ EKLEMESİ:
        # Eğer önümüz nispeten boşsa (0.6), sensör ne derse desin TAM GAZ GİT.
        # Bu, Professor X'i yenen kısımdır.
        if s_front > 0.6:
            translation = 1.0
            # Hafif yalpalanma (wobble) ekle ki düz çizgide iz bırakmasın, alanı tarasın
            rotation += 0.1 if self.memory % 10 < 5 else -0.1
            self.memory += 1 # Memory'yi wobble sayacı olarak da kullanıyoruz (20-40 arası döner)

        return translation, rotation, False