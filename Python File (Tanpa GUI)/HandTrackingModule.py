import cv2
import mediapipe as mp
import time
import math


class HandDetector:

    '''Menemukan Tangan dengan menggunakan library mediapipe
    yang membaca landmark tangan dalam format piksel'''

    def __init__(self, mode=False, max_hands=2, max_detection_con=0.5, min_detection_con=0.5):
        self.mode = mode
        self.maxHands = max_hands
        self.detectionCon = max_detection_con
        self.trackCon = min_detection_con
        self.key_points = [4, 8, 12, 16, 20]
        self.active = 0
        self.fingers = []
        self.lm_list = []

        # Detect The Hands
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, hand_no=0, draw=True, color=(255, 0, 255), z_axis=False):
        self.lm_list = []
        cx, cy = 0, 0

        # Checking Multiple Hand
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            for i, lm in enumerate(my_hand.landmark):
                h, w, c = img.shape
                if not z_axis:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.lm_list.append([i, cx, cy])
                elif z_axis:
                    cx, cy, cz = int(lm.x * w), int(lm.y * h), round(lm.z, 3)
                    self.lm_list.append([i, cx, cy, cz])
                if draw:
                    cv2.circle(img, (cx, cy), 5, color, cv2.FILLED)
        return self.lm_list

    def fingers_up(self):
        fingers = []

        # Thumb
        if self.lm_list[self.key_points[0]][1] > self.lm_list[self.key_points[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers
        for i in range(1, 5):
            if self.lm_list[self.key_points[i]][2] < self.lm_list[self.key_points[i] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def find_distance(self, p1, p2, img, draw=True):

        '''Menentukan jarak antara dua landmark berdasarkan
         nomor indeks'''

        # Get Distance Key Points
        x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
        x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            # Draw Dot and Line on Key Points
            cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)

        # Distance Two Points
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]


def main():
    p_time = 0
    cap = cv2.VideoCapture(0)
    detector = HandDetector(max_hands=2)
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.find_hands(img)
        lm_list = detector.find_position(img, z_axis=True, draw=False)
        if len(lm_list) != 0:
            print(lm_list[4])

        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time

        cv2.putText(img, f'FPS:{int(fps)}', (480, 50), cv2.FONT_ITALIC, 1, (255, 255, 255), 2)

        cv2.imshow("Image", img)
        cv2.waitKey(1)
        if cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) < 1:
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()