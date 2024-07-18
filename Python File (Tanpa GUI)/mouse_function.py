import cv2
import pyautogui
import autopy
import numpy as np
import HandTrackingModule as Htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
pyautogui.FAILSAFE = False

# Memannggil Class dari modul HandTrackingModule
detector = Htm.HandDetector(max_hands=2, max_detection_con=0.85, min_detection_con=0.8)

# Setting Lebar dan tinggi frame
w_cam, h_cam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, w_cam)
cap.set(4, h_cam)
frame_reduction = 100

# Size Screen (1366 x 768)
w_scr, h_scr = autopy.screen.size()
p_time = 0
p_locX, p_locY = 0, 0
c_locX, c_locY = 0, 0


def set_scroll(set_fingers, set_lm_list, set_img):
    #Scroll up dengan jari telunjuk
    if set_fingers == [0, 1, 0, 0, 0]:
        cv2.circle(set_img, (set_lm_list[8][1], set_lm_list[8][2]), 7, (0, 255, 0), cv2.FILLED)
        pyautogui.scroll(100)

    #Scroll down dengan jari telunjuk dan jari tengah
    elif set_fingers == [0, 1, 1, 0, 0]:
        cv2.circle(set_img, (set_lm_list[8][1], set_lm_list[8][2]), 7, (0, 255, 0), cv2.FILLED)
        cv2.circle(set_img, (set_lm_list[12][1], set_lm_list[12][2]), 7, (0, 255, 0), cv2.FILLED)
        pyautogui.scroll(-100)


def set_volume(set_img):
    # Set Audio
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # Mengatur slide bar, min/max vol
    h_min = 50
    h_max = 300
    slide_bar = 400
    max_bar = 150
    percent_max = 100
    percent_min = 4

    # Jarak Antara Ibu Jari dan Kelingking
    length, set_img, line_loc = detector.find_distance(4, 20, set_img)

    # Set Volume Bar
    vol_bar = np.interp(length, [h_min, h_max], [slide_bar, max_bar])
    vol_per = np.interp(length, [h_min, h_max], [percent_min, percent_max])

    # Mengatur kenaikan persen dari volume
    smoothness = 4
    vol_per = smoothness * round(vol_per / smoothness)
    volume.SetMasterVolumeLevelScalar(vol_per / 100, None)

    if vol_per == 0:
        cv2.circle(set_img, (line_loc[4], line_loc[5]), 11, (0, 0, 255), cv2.FILLED)

    elif vol_per == 100:
        cv2.circle(set_img, (line_loc[4], line_loc[5]), 11, (0, 0, 255), cv2.FILLED)

    # Showing Bar Volume
    cv2.rectangle(set_img, (30, 150), (55, 400), (255, 255, 255), 3)
    cv2.rectangle(set_img, (30, int(vol_bar)), (55, 400), (255, 255, 255), cv2.FILLED)
    cv2.putText(set_img, f'{int(vol_per)}%', (25, 430), cv2.FONT_HERSHEY_COMPLEX, 0.9, (255, 255, 255), 3)


def set_cursor(set_fingers, set_lm_list, set_img):
    global p_locX, p_locY, c_locX, c_locY, w_cam, w_scr, frame_reduction

    # Posisi Jari Telunjuk
    x1, y1 = set_lm_list[8][1], set_lm_list[8][2]

    # Konversi koordinat karena screen yang dipakai dalam cv adalah 640x840 sedangan yg dipakai di laptop adalah 1366x768
    x = np.interp(x1, (frame_reduction, w_cam - frame_reduction), (0, w_scr))
    y = np.interp(y1, (frame_reduction, w_cam - frame_reduction), (0, w_scr))

    # Memperhalus Gerakan Cursor
    c_locX = p_locX + (x - p_locX) / 4
    c_locY = p_locY + (y - p_locY) / 4

    # Membuat Dot di Ujung Jari Tangan (Ibu Jari, Jari Telunjuk, Jari Tengah, Jari Kelingking)
    cv2.circle(set_img, (set_lm_list[20][1], set_lm_list[20][2]), 7, (0, 255, 0), cv2.FILLED)
    cv2.circle(set_img, (set_lm_list[8][1], set_lm_list[8][2]), 7, (0, 255, 0), cv2.FILLED)
    cv2.circle(set_img, (set_lm_list[4][1], set_lm_list[4][2]), 7, (0, 255, 0), cv2.FILLED)

    # Koordinat Untuk Menggerakan Mouse
    autopy.mouse.move(w_scr - c_locX, c_locY)
    p_locX, p_locY = c_locX, c_locY

    # Klik kiri
    if set_fingers == [0, 1, 0, 0, 0]:
        cv2.circle(set_img, (set_lm_list[4][1], set_lm_list[4][2]), 10, (0, 0, 255), cv2.FILLED)  # thumb
        pyautogui.click()

    # Klik Kanan
    if set_fingers[1] == 1 and set_fingers[4] == 1:
        cv2.circle(set_img, (set_lm_list[20][1], set_lm_list[20][2]), 10, (0, 0, 255), cv2.FILLED)
        pyautogui.click(button='right')
