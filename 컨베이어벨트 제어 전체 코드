import RPi.GPIO as GPIO
from hx711 import HX711
import serial, json, ssl, time, sys

ENDPOINT = "avznflen5h2qi-ats.iot.ap-southeast-2.amazonaws.com"
THING_NAME = 'raspberrypi'
CERTPATH =  "/home/pi/Desktop/raspProjects/awsDocuments/raspberrypi.cert.pem" # cert파일 경로
KEYPATH = "/home/pi/Desktop/raspProjects/awsDocuments/raspberrypi.private.key" # key 파일 경로
CAROOTPATH = "/home/pi/Desktop/raspProjects/awsDocuments/root-CA.crt" # RootCaPem 파일 경로
TOPIC = 'test' #주제

mqtt_client = mqtt.Client(client_id=THING_NAME)
mqtt_client.on_connect = on_connect
mqtt_client.tls_set(CAROOTPATH, certfile= CERTPATH, keyfile=KEYPATH, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
mqtt_client.connect(ENDPOINT, port=8883)
mqtt_client.loop_start()

# 로드셀 기본설정
hx = HX711(20, 21)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(92)              # 로드셀의 무게단위 설정하기
hx.reset()
hx.tare()

# 라즈베리파이의 uart2, uart3, uart4를 열기
uart2 = serial.Serial("/dev/ttyAMA1", baudrate=9600)
uart3 = serial.Serial("/dev/ttyAMA2", baudrate=9600)
uart4 = serial.Serial("/dev/ttyAMA3", baudrate=9600)

# tof10120센서에서 거리 데이터를 읽는 함수
def read_distance(uart):
    # 0x00번지부터 2바이트 읽기
    uart.write(b"\x00\x02")
    data = uart.read(2)
    # 상위 바이트와 하위 바이트를 합치기
    distance = (data[0] << 8) + data[1]
    return distance

# 모터 입출력핀 설정.
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

motor1 = GPIO.PWM(15, 50) # 50Hz
motor1.start(50)
motor2 = GPIO.PWM(18, 50) # 
motor2.start(50)
motor3 = GPIO.PWM(20, 50) # 컨베이어벨트위 먼저 있는 모터
motor3.start(50)
motor4 = GPIO.PWM(21, 50) # 컨베이어벨트위 나중에 있는 모터
motor4.start(50)


while True:
	boxWeight = hx.get_weight(5)  # 로드셀에서 상자의 무게 측정하기
	while boxWeight:    # 로드셀 위에 상자가 놓여지면(상자의 무게가 0이 아닐때) 반복문 실행
		# tof10120센서에서 가로, 세로, 높이값 구하기
		distance1 = read_distance(uart2)
		distance2 = read_distance(uart3)
		distance3 = read_distance(uart4)
		boxVolume = distance1 * distance2 * distance3 # 상자의 부피 구하기
		
		if boxVolume > 500:                       
			print("<<부피가 너무 큰 물류>>")
			print("(1)번 분류장으로 이동중...")
			time.sleep(1)
			motor3.ChangeDutyCycle(2)
			time.sleep(1)
			motor3.ChangeDutyCycle(7)
			time.sleep(1)
			print("(1)번 분류장으로 분류 완료!!")
		elif boxWeight < 50 :
			print("<<가벼운 물류>>")
			print("(2)번 분류장으로 이동중...")
			time.sleep(2)
			motor4.ChangeDutyCycle(2)
			time.sleep(1)
			motor4.ChangeDutyCycle(7)
			time.sleep(1)
			print("(2)번 분류장으로 분류 완료!!")
		else:
			print("<<무거운 물류>>")
			print("(3)번 분류장으로 이동중...")
			time.sleep(1)
			print("(3)번 분류장으로 분류 완료!!")
		print("----------------------------------------------")
		def on_connect(mqttc, obj, flags, rc):
  		    if rc == 0: # 연결 성공
				print("라즈베리파이와 aws가 연결되었습니다!!")
				#print("----------------------------------------------")
		 data = {                               # 변수들의 값을 JSON 형식으로 변환
			"distance1": distance1,
			"distance2": distance2,
			"distance3": distance3,
			"section1": section1,
			"section2": section2,
			"section3": section3,
			"boxVolume": boxVolume
			}
        	payload = json.dumps(data)  # JSON 객체를 문자열로 인코딩
        	client.publish(topic, payload, qos=1) # 토픽에 메시지 발행
