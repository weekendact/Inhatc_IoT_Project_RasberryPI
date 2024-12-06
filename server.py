from flask import Flask, request
import RPi.GPIO as GPIO
import threading
import time

# GPIO 핀 설정
MOTOR_PIN1 = 27  # 모터 드라이버 IN1
MOTOR_PIN2 = 22  # 모터 드라이버 IN2
LED_PIN = 17     # LED 연결 핀
PIEZO_PIN = 10   # 피에조 부저 핀

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN1, GPIO.OUT)
GPIO.setup(MOTOR_PIN2, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(PIEZO_PIN, GPIO.OUT)

# Flask 애플리케이션 생성
app = Flask(__name__)

# 하드웨어 상태 관리
shutdown_event = threading.Event()
shutdown_event.set()  # 기본적으로 하드웨어를 정지 상태로 설정

# LED 스레드
def led_worker():
    while True:
        shutdown_event.wait()  # 신호가 오기 전까지 대기
        GPIO.output(LED_PIN, GPIO.HIGH)
        print("[LED] 켜짐")
        while shutdown_event.is_set():
            time.sleep(0.1)  # 하드웨어 유지
        GPIO.output(LED_PIN, GPIO.LOW)
        print("[LED] 꺼짐")

# 모터 스레드
def motor_worker():
    while True:
        shutdown_event.wait()  # 신호가 오기 전까지 대기
        GPIO.output(MOTOR_PIN1, GPIO.HIGH)
        GPIO.output(MOTOR_PIN2, GPIO.LOW)
        print("[모터] 작동 시작")
        while shutdown_event.is_set():
            time.sleep(0.1)  # 하드웨어 유지
        GPIO.output(MOTOR_PIN1, GPIO.LOW)
        GPIO.output(MOTOR_PIN2, GPIO.LOW)
        print("[모터] 작동 중지")

# 피에조 부저 스레드
def piezo_worker():
    while True:
        shutdown_event.wait()  # 신호가 오기 전까지 대기
        print("[피에조] 부저 울림 시작")
        while shutdown_event.is_set():
            GPIO.output(PIEZO_PIN, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(PIEZO_PIN, GPIO.LOW)
            time.sleep(0.1)
        GPIO.output(PIEZO_PIN, GPIO.LOW)
        print("[피에조] 부저 울림 중지")

# Flask 엔드포인트
@app.route("/action", methods=["POST"])
def action():
    global shutdown_event
    data = request.json
    print(f"요청 데이터: {data}")  # 받은 데이터를 출력해 디버깅
    if data and data.get("status") == "detected":
        print("[신호 수신] 화재 감지 신호")
        shutdown_event.set()  # 하드웨어 작동 시작
        threading.Timer(5.0, stop_hardware).start()  # 5초 후 작동 중지 타이머
    else:
        print("[신호 수신] 잘못된 데이터 또는 감지되지 않음")
    return "OK", 200

# 하드웨어 작동 중지
def stop_hardware():
    global shutdown_event
    print("[타이머 만료] 하드웨어 작동 중지")
    shutdown_event.clear()

if __name__ == "__main__":
    # 하드웨어 스레드 시작
    led_thread = threading.Thread(target=led_worker, daemon=True)
    motor_thread = threading.Thread(target=motor_worker, daemon=True)
    piezo_thread = threading.Thread(target=piezo_worker, daemon=True)
    
    led_thread.start()
    motor_thread.start()
    piezo_thread.start()

    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("프로그램 종료 중...")
    finally:
        shutdown_event.clear()
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.output(MOTOR_PIN1, GPIO.LOW)
        GPIO.output(MOTOR_PIN2, GPIO.LOW)
        GPIO.output(PIEZO_PIN, GPIO.LOW)
        GPIO.cleanup()
