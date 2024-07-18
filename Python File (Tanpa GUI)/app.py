import sys
import cv2
import time
import mouse_function as mf


def main_function():
    cap = mf.cap
    detector = mf.detector
    p_time = 0
    mode = ""
    while cap.isOpened():
        # Mencari landmarks tangan dengan memmanggil modul
        success, img = cap.read()
        img = detector.find_hands(img)
        lm_list = detector.find_position(img, z_axis=True, draw=False)
        fingers = []

        # Jika jari tangan tidak di tekuk semua  maka akan menjalankan baris code yang dibawah
        if len(lm_list) != 0:
            fingers = detector.fingers_up()

            '''Info untuk isi list yang berada di variable 
            fingers [Ibu Jari, Jari Telunjuk, Jari Tengah, Jari Manis, Jari Kelingking]'''

            # Jika jari di tekuk semua atau tidak ada yang berdiri maka akan memasuki mode netral
            if (fingers == [0, 0, 0, 0, 0]) & (detector.active == 0):
                mode = 'N'

            # Jika jari telunjuk atau (jari tengah dan jari telunjuk) berdiri maka akan memasuki mode scroll
            elif (fingers == [0, 1, 0, 0, 0] or fingers == [0, 1, 1, 0, 0]) & (detector.active == 0):
                mode = 'Scroll'
                detector.active = 1

            # Jika ibu jari dan jari kelingking berdiri maka akan memasuki mode volume
            elif (fingers == [1, 0, 0, 0, 1]) & (detector.active == 0):
                mode = 'Volume'
                detector.active = 1

            # Jika ibu jari dan jari telunjuk berdiri maka akan memasuki mode cursor
            elif (fingers == [1, 1, 0, 0, 0]) & (detector.active == 0):
                mode = 'Cursor'
                detector.active = 1

            elif (fingers == [0, 1, 1, 1, 0]) & (detector.active == 0):
                mode = 'Break'
                detector.active = 1

        # Exit Program
        if mode == 'Break':
            detector.active = 1
            if fingers == [0, 0, 0, 0, 0]:
                detector.active = 0
                mode = 'N'
                print(mode)
            else:
                if fingers == [0, 1, 1, 1, 0]:
                    break

        # Scroll
        if mode == 'Scroll':
            detector.active = 1
            if fingers == [0, 0, 0, 0, 0]:
                detector.active = 0
                mode = 'N'
                print(mode)
            else:
                if len(lm_list) != 0:
                    mf.set_scroll(fingers, lm_list, img)
            print(fingers)

        # Volume
        elif mode == 'Volume':
            detector.active = 1
            if len(lm_list) != 0:
                if fingers[-1] == 0:
                    detector.active = 0
                    mode = 'N'
                    print(mode)
                else:
                    mf.set_volume(img)
            print(fingers)

        # Cursor
        elif mode == 'Cursor':
            detector.active = 1
            if fingers == [0, 0, 0, 0, 0]:
                detector.active = 0
                mode = 'N'
                print(mode)
            else:
                if len(lm_list) != 0:
                    mf.set_cursor(fingers, lm_list, img)
            print(fingers)

        # Menampilkan FPS
        c_time = time.time()
        fps = 1 / ((c_time + 0.01) - p_time)
        p_time = c_time
        frame_flip = cv2.flip(img, 1)
        cv2.putText(frame_flip, f'FPS:{int(fps)}', (480, 50), cv2.FONT_ITALIC, 1, (255, 255, 255), 2)

        # Menampilkan Frame
        cv2.imshow("Virtual Mouse", frame_flip)
        cv2.waitKey(1)
        if cv2.getWindowProperty("Virtual Mouse", cv2.WND_PROP_VISIBLE) < 1:
            sys.exit()


if __name__ == "__main__":
    main_function()

