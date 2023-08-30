import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO 
import time, json, ssl, sys, serial
from hx711 import HX711

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 

# HX711 객체 생성
hx = HX711(21, 20) # DT와 SCK가 연결된 GPIO 핀 번호 할당
hx.set_offset(0) # 초기값 설정
hx.set_reference_unit(228) # 비율 설정 (1g일 때의 수치)
hx.reset() # 센서 초기화
hx.tare() # 센서 준비

# 라즈베리파이의 uart2, 3, 4를 열기
uart3 = serial.Serial("/dev/ttyAMA1", baudrate=9600)
uart4 = serial.Serial("/dev/ttyAMA2", baudrate=9600)
uart5 = serial.Serial("/dev/ttyAMA3", baudrate=9600)


ENDPOINT = "avznflen5h2qi-ats.iot.ap-southeast-2.amazonaws.com"
THING_NAME = 'raspberrypi'
CERTPATH =  "/home/pi/Desktop/raspProjects/awsDocuments/raspberrypi.cert.pem" # cert파일 경로
KEYPATH = "/home/pi/Desktop/raspProjects/awsDocuments/raspberrypi.private.key" # key 파일 경로
CAROOTPATH = "/home/pi/Desktop/raspProjects/awsDocuments/root-CA.crt" # RootCaPem 파일 경로
TOPIC = 'conveyerBelt' #주제


# aws와 연결되었을때 알림 함수 생성
def on_connect(mqttc, obj, flags, rc):
		if rc == 0: # 연결 성공
			print("라즈베리파이와 aws가 연결되었습니다!!")
			print("--------------------------------")
# aws와 연결 설정
mqtt_client = mqtt.Client(client_id=THING_NAME)
mqtt_client.on_connect = on_connect
mqtt_client.tls_set(CAROOTPATH,certfile=CERTPATH,keyfile=KEYPATH,tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
mqtt_client.connect(ENDPOINT, port=8883)

# tof10120센서에서 거리 데이터를 읽는 함수
def read_distance(uart):
    # 0x00번지부터 2바이트 읽기
    uart.write(b"\x00\x02")
    data = uart.read(2)
    # 상위 바이트와 하위 바이트를 합치기
    distance = data[0] * 256 + data[1]
    return distance

section1=0
section2=0
section3=0

while True:
	
	# 로드셀에서 무게 측정하기
	val = hx.get_weight(5) # 센서 값 읽기
	weight = val / 1000.0    # 무게 단위로 변환 (g)
	print("무게: %.2f g" % boxWeight) # 소수점 둘째 자리까지 출력
	hx.power_down() # 센서 초기화
	hx.power_up()
	time.sleep(1.5)
	
	
	# tof10120센서1, 2, 3에서 거리 데이터 읽기
	distance1 = read_distance(uart3)
	distance2 = read_distance(uart4)
	distance3 = read_distance(uart5)
	# 거리 데이터 곱하기
	boxVolume = distance1 * distance2 * distance3
	time.sleep(1.5)

	print("!!컨베이어벨트 위로 물류가 이동했습니다!!")
	if boxVolume > 1000:
		print("<<부피가 너무 큰 물류>>")
		print("(1)번 분류장으로 이동중...")
		print("(1)번 분류장으로 이동 완료!!")
		section1+=1
	elif boxWeight < 50:
		print("<<가벼운 물류>>")
		print("(2)번 분류장으로 이동중...")
		print("(2)번 분류장으로 이동 완료!!")
		section2+=1
	else:
		print("<<무거운 물류>>")
		print("(3)번 분류장으로 이동중...")
		print("(3)번 분류장으로 이동 완료!!")
		section3+=1
	print(">>>>물류현황<<<<")
	time.sleep(1)
	print("(1)번 분류장 : %d개" % section1)
	print("(2)번 분류장 : %d개" % section2)
	print("(3)번 분류장 : %d개" % section3)
	print("--------------------------------")
	mqtt_client.loop_start()
	data = {                               # 변수들의 값을 JSON 형식으로 변환
			"section1": section1,
			"section2": section2,
			"section3": section3,
			"boxVolume": boxVolume
			}
	payload = json.dumps(data)  # JSON 객체를 문자열로 인코딩
	mqtt_client.publish(TOPIC, payload, qos=1) # 토픽에 메시지 발행
	time.sleep(1)
	print(">>라즈베리파이에서 aws서버로 데이터 전송이 완료되었습니다<<")
	print("--------------------------------")
