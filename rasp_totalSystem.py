import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO 
import time, json, ssl

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

mqtt_client = mqtt.Client(client_id=THING_NAME)
mqtt_client.on_connect = on_connect              
mqtt_client.tls_set(CAROOTPATH,certfile=CERTPATH,keyfile=KEYPATH,tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
mqtt_client.connect(ENDPOINT, port=8883)

	 

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 

section1=0
section2=0
section3=0

while True:
	boxVolume=int(input("상자의 부피를 단위(cm^3)를 제외하고 입력하시오 : "))
	boxWeight=int(input("상자의 무게를 단위(g)를 제외하고 입력하시오 : "))
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
