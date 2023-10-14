import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

ServoPin1 = 21
ServoPin2 = 20
ServoPin3 = 16
ServoPin4 = 12

GPIO.setup(ServoPin1, GPIO.OUT)
motor1 = GPIO.PWM(ServoPin1, 50)
motor1.start(50)
GPIO.setup(ServoPin2, GPIO.OUT)
motor2 = GPIO.PWM(ServoPin2, 50)
motor2.start(50)
GPIO.setup(ServoPin3, GPIO.OUT)
motor3 = GPIO.PWM(ServoPin3, 50)
motor3.start(50)
GPIO.setup(ServoPin4, GPIO.OUT)
motor4 = GPIO.PWM(ServoPin4, 50)
motor4.start(50)

while True:
	boxVolume=int(input("상자의 부피를 단위(cm^3)를 제외하고 입력하시오 : "))
	boxWeight=int(input("상자의 무게를 단위(g)를 제외하고 입력하시오 : "))
	motor1.ChangeDutyCycle(2)
	motor1.ChangeDutyCycle(12)            
	time.sleep(1)
	motor2.ChangeDutyCycle(12)
	motor2.ChangeDutyCycle(2)
	time.sleep(1)
	print("!!컨베이어벨트 위로 물류가 이동했습니다!!")
	if boxVolume > 1000:
		print("<<부피가 너무 큰 물류>>")
		print("(1)번 분류장으로 이동중...")
		time.sleep(5)
		motor3.ChangeDutyCycle(2)
		time.sleep(1)
		motor3.ChangeDutyCycle(7)
		time.sleep(1)
		print("(1)번 분류장으로 이동 완료!!")
	elif boxWeight < 50:
		print("<<가벼운 물류>>")
		print("(2)번 분류장으로 이동중...")
		time.sleep(5)
		motor4.ChangeDutyCycle(2)
		time.sleep(1)
		motor4.ChangeDutyCycle(7)
		time.sleep(1)
		print("(2)번 분류장으로 이동 완료!!")
	else:
		print("<<무거운 물류>>")
		print("(3)번 분류장으로 이동중...")
		print("(3)번 분류장으로 이동 완료!!")