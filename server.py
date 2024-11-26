from flask import Flask, request
import RPi.GPIO as GPIO

# GPIO 핀 설정
MOTOR_PIN1 = 27  # 모터 드라이버 IN1
MOTOR_PIN2 = 22  # 모터 드라이버 IN2
LED_PIN = 17     # LED 연결 핀

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN1, GPIO.OUT)
GPIO.setup(MOTOR_PIN2, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)

# Flask 애플리케이션 생성
app = Flask(__name__)

@app.route("/action", methods=["POST"])
def action():
    data = request.json
    print(f"요청 데이터: {data}")  # 받은 데이터를 출력해 디버깅
    if data and data.get("status") == "detected":
        # 감지된 경우 LED와 모터 켜기
        GPIO.output(LED_PIN, GPIO.HIGH)
        GPIO.output(MOTOR_PIN1, GPIO.HIGH)
        GPIO.output(MOTOR_PIN2, GPIO.LOW)
        print("사람 감지: LED와 모터 작동")
    else:
        # 감지되지 않은 경우 LED와 모터 끄기
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.output(MOTOR_PIN1, GPIO.LOW)
        GPIO.output(MOTOR_PIN2, GPIO.LOW)
        print("감지되지 않음: LED와 모터 꺼짐")
    return "OK", 200


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("종료 중...")
    finally:
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.output(MOTOR_PIN1, GPIO.LOW)
        GPIO.output(MOTOR_PIN2, GPIO.LOW)
        GPIO.cleanup()

