import cv2
import numpy as np
import serial
import time
import serial.tools.list_ports
from datetime import datetime


# -------------------------------------
# 로그 저장
# -------------------------------------
def write_log(message):
    with open("water_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {message}\n")


# -------------------------------------
# 콘솔 상태 출력
# -------------------------------------
def print_status(mode, state_text, pixels):
    b_pix, g_pix, bl_pix = pixels

    if mode == "blink_red":
        led_text = "RED BLINK"
    elif mode == "blink_blue":
        led_text = "BLUE BLINK"
    elif mode == "normal":
        led_text = "GREEN"
    else:
        led_text = "OFF"

    print("\n================ 상태 업데이트 ================")
    print(f"현재 상태: {state_text}")
    print(f"LED 상태: {led_text}")
    print(f"픽셀값 → 갈색:{b_pix} | 초록:{g_pix} | 파랑:{bl_pix}")
    print("================================================\n")


# -------------------------------------
# LED 제어
# -------------------------------------
def send_led(r, g, b):
    try:
        data = f"RGB={r},{g},{b}\n"
        my_serial.write(data.encode())
    except:
        pass


def blink_led(r, g, b, delay=0.2):
    send_led(r, g, b)
    time.sleep(delay)
    send_led(0, 0, 0)
    time.sleep(delay)


# -------------------------------------
# 물 색깔 감지
# -------------------------------------
def detect_water_color(frame):

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    brown_low = np.array([0, 30, 20])
    brown_high = np.array([30, 255, 255])

    green_low = np.array([25, 40, 20])
    green_high = np.array([95, 255, 255])

    blue_low = np.array([85, 40, 20])
    blue_high = np.array([140, 255, 255])

    brown_mask = cv2.inRange(hsv, brown_low, brown_high)
    green_mask = cv2.inRange(hsv, green_low, green_high)
    blue_mask = cv2.inRange(hsv, blue_low, blue_high)

    b_pix = np.sum(brown_mask)
    g_pix = np.sum(green_mask)
    bl_pix = np.sum(blue_mask)

    threshold = 2000

    if max(b_pix, g_pix, bl_pix) < threshold:
        return None, "none", (b_pix, g_pix, bl_pix)

    if b_pix == max(b_pix, g_pix, bl_pix):
        return (255, 0, 0), "blink_red", (b_pix, g_pix, bl_pix)

    elif g_pix == max(b_pix, g_pix, bl_pix):
        return (0, 0, 255), "blink_blue", (b_pix, g_pix, bl_pix)

    else:
        return (0, 255, 0), "normal", (b_pix, g_pix, bl_pix)


# -------------------------------------
# 메인
# -------------------------------------
def main():

    global last_blink, show_text
    last_blink = time.time()
    show_text = True

    camera = cv2.VideoCapture(0)
    camera.set(3, 640)
    camera.set(4, 480)

    while True:
        ret, frame = camera.read()
        if not ret:
            continue

        led_color, mode, pixels = detect_water_color(frame)
        b_pix, g_pix, bl_pix = pixels

        # 상태 텍스트 처리
        if mode == "blink_red":
            state_text = "오염(갈색)"
            blink_led(255, 0, 0)
            write_log(f"[오염/갈색] LED=RED BLINK | 픽셀={pixels}")
            show_state = "🔴 RED"
            text_color = (0, 0, 255)

        elif mode == "blink_blue":
            state_text = "녹조(초록)"
            blink_led(0, 0, 255)
            write_log(f"[녹조/초록] LED=BLUE BLINK | 픽셀={pixels}")
            show_state = "🔵 BLUE"
            text_color = (255, 0, 0)

        elif mode == "normal":
            state_text = "정상(파랑)"
            send_led(0, 255, 0)
            write_log(f"[정상/파랑] LED=GREEN | 픽셀={pixels}")
            show_state = "🟢 GREEN"
            text_color = (0, 255, 0)

        else:
            state_text = "감지 실패"
            send_led(0, 0, 0)
            write_log(f"[감지 실패] LED=OFF | 픽셀={pixels}")
            show_state = "⚪ NONE"
            text_color = (200, 200, 200)

        # 🔥 텍스트 깜박임(0.4초 간격)
        if time.time() - last_blink > 0.4:
            show_text = not show_text
            last_blink = time.time()

        # 🔥 깜박이는 텍스트 출력
        if show_text:
            cv2.putText(frame, show_state, (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.4, text_color, 3)

        # 콘솔 출력
        print_status(mode, state_text, pixels)

        cv2.imshow("Water Monitor", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()


# -------------------------------------
# Arduino 자동 연결
# -------------------------------------
if __name__ == "__main__":

    ports = list(serial.tools.list_ports.comports())
    my_serial = None

    for p in ports:
        if "Arduino" in p.description:
            print("Arduino 연결됨:", p.device)
            my_serial = serial.Serial(p.device, 9600, timeout=1)
            time.sleep(2)
            break

    if my_serial:
        print("===========================")
        print("     WATER COLOR LOGGER    ")
        print(" 🔴 오염 → RED BLINK")
        print(" 🟢 정상 → GREEN")
        print(" 🔵 녹조 → BLUE BLINK")
        print(" ⚪ 감지 실패 → NONE")
        print(" water_log.txt에 저장됨")
        print("===========================")
        main()

    else:
        print("❌ Arduino 연결 실패")
  