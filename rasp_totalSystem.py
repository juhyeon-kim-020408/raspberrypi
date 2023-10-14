import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO 
import time, json, ssl, sys, serial


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 
EMULATE_HX711=False

# 레이저 모듈 초기 설정
GPIO.setup(14, GPIO.OUT)
GPIO.output(14, GPIO.LOW)
GPIO.setup(15, GPIO.OUT)
GPIO.output(15, GPIO.LOW)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.LOW)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.LOW)

# HX711 설정
reference_unit = -469.004
if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

hx = HX711(17, 27)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(reference_unit) # 비율 설정 (1g일 때의 수치)
hx.reset() # 센서 초기화
hx.tare() # 센서 준비

# 라즈베리파이의 uart2, 3, 4, 5를 열기
uart2 = serial.Serial("/dev/ttyAMA1", baudrate=9600)     # 상부센서
uart3 = serial.Serial("/dev/ttyAMA2", baudrate=9600)     # 측면센서
uart4 = serial.Serial("/dev/ttyAMA3", baudrate=9600)     # 측면센서
uart5 = serial.Serial("/dev/ttyAMA4", baudrate=9600)     # 후방센서(tof10120)

a = 38   # 로드셀부터 상부센서까지의 거리
b = 16  # 좌측센서부터 로드셀 중앙까지의 거리
c = 11 # 후방센서부터 로드셀 중앙까지의 거리 


# aws활성화
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

sectionA = 0   # 각 구역에 몇 개의 물류가 있는지 카운트
sectionB = 0
sectionC = 0
sectionDecision = ""

# 서보모터 기본설정
ServoPin1 = 20
ServoPin2 = 21
ServoPin3 = 26
ServoPin4 = 19

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
	# 거리값을 저장할 리스트 생성(초기화)
	distanceList1 = []  # 높이
	distanceList2 = []   # 가로반
	distanceList3 = []   # 가로반
	distanceList4 = []   # 세로
	weightList = [] # 로드셀 리스트 생성
	time.sleep(1)

	
	# 레이저모듈 ON
	GPIO.output(14, GPIO.HIGH)
	GPIO.output(15, GPIO.HIGH)
	GPIO.output(18, GPIO.HIGH)
	GPIO.output(23, GPIO.HIGH)
	time.sleep(1)
	

	while True:                     # 로드셀 위에 물체가 올라가야 다음단계를 실행시키는 반복문(1차 거름망 반복문)
		print("물류감지중...")
		val = hx.get_weight(1) 
		if val > 50:
			break
		else:
			pass
	while True:                  
		val = hx.get_weight(1)   # 로드셀 위에 물체가 감지되면 본격 코드 실행
		if val > 50:
			pass
		else:
			break

		print("물류감지완료!!")
		hx.power_down()   # 로드셀 초기화
		hx.power_up()
		
		# n번 반복하면서 센서로부터 데이터 읽기
		for i in range(10):
			data1 = uart2.readline().decode().strip()
			data2 = uart3.readline().decode().strip()
			data3 = uart4.readline().decode().strip()
			data4 = uart5.readline().decode().strip()
			weight = hx.get_weight(1)
			
			# 데이터를 정수로 변환하여 거리 값으로 처리
			distance1 = a - int(data1) 
			distance2 = b - int(data2)
			distance3 = b - int(data3)
			distance4 = c - int(data4[0:-2])/10
			
			# 거리값을 리스트에 추가
			distanceList1.append(distance1)
			distanceList2.append(distance2)
			distanceList3.append(distance3)
			distanceList4.append(distance4)	

			weightList.append(weight) # 리스트에 추가
				
			# 0.1초에 한 번 측정
			time.sleep(0.1)
		hx.power_down()   # 로드셀 초기화
		hx.power_up()
			
		# n개의 거리값의 평균 계산
		distanceAverage1 = sum(distanceList1) / len(distanceList1)
		distanceAverage2 = sum(distanceList2) / len(distanceList2)
		distanceAverage3 = sum(distanceList3) / len(distanceList3)
		distanceAverage4 = 2 * (sum(distanceList4) /  len(distanceList4))
		boxVolume = int(distanceAverage1 * (distanceAverage2 + distanceAverage3) * distanceAverage4)

		# 레이저모듈 OFF
		GPIO.output(14, GPIO.LOW)
		GPIO.output(15, GPIO.LOW)
		GPIO.output(18, GPIO.LOW)
		GPIO.output(23, GPIO.LOW)
		time.sleep(1)
		
		motor1.ChangeDutyCycle(2)         # 컨베이어벨트 위로 물류를 올리는 단계
		motor2.ChangeDutyCycle(12)  
		time.sleep(1)
		motor1.ChangeDutyCycle(12)      
		motor2.ChangeDutyCycle(2)       
		time.sleep(1)

		print("!!컨베이어벨트 위로 물류가 이동했습니다!!")

		if boxVolume > 1000:
			print("<<부피가 너무 큰 물류>>")
			print("(C) 분류장으로 이동중...")
			time.sleep(5)
			print("(C)번 분류장으로 이동 완료!!")
			sectionDecision = "C"
			sectionC+=1
		elif boxWeight > 50:
			print("<<무거운 물류>>")
			print("(A)번 분류장으로 이동중...")
			time.sleep(2.2)                      # 시간은 벨트 속도 고려해서 적당히 넣기
			motor3.ChangeDutyCycle(2)                 # 두번째 분류장으로 가는 모터제어 과정
			time.sleep(1)
			motor3.ChangeDutyCycle(7)
			time.sleep(1)
			print("(A)번 분류장으로 이동 완료!!")
			sectionDecision = "A"
			sectionA+=1
		else:
			print("<<가벼운 물류>>")
			print("(B)번 분류장으로 이동중...")
			time.sleep(5.3)                      # 시간은 벨트 속도 고려해서 적당히 넣기
			motor4.ChangeDutyCycle(2)                 # 두번째 분류장으로 가는 모터제어 과정
			time.sleep(1)
			motor4.ChangeDutyCycle(7)
			time.sleep(1)                   # 시간은 벨트 속도 고려해서 적당히 넣기
			print("(B)번 분류장으로 이동 완료!!")
			sectionDecision = "B"
			sectionB+=1
			
		percentCondition = (sectionA + sectionB + sectionC) * 3.33  
		
		print(">>>>물류현황<<<<")
		print("(A)번 분류장 : %d개" % sectionA)
		print("(B)번 분류장 : %d개" % sectionB)
		print("(C)번 분류장 : %d개" % sectionC)
		print("현재 물류 목표구역 : %s" % sectionDecision)
		print("상부센서 : %.2f" % distanceAverage1)
		print("측부센서1 : %.2f" % distanceAverage2)
		print("측부센서2 : %.2f" % distanceAverage3)
		print("후방센서 : %.2f" % distanceAverage4)
		print("현재 물류의 부피 : %.2f" % boxVolume + "cm^3")
		print("현재 물류의 무게 : %.2f" % boxWeight + "g")
		print("현재 물류 목표치 달성률 : %.2f" % percentCondition + "%")
		print("--------------------------------")
		mqtt_client.loop_start()

		# DB로 보내려고 str문자열 형으로 형변환
		percentCondition = str((sectionA + sectionB + sectionC) * 3.33)   # 총 물류 30개 중 현재 퍼센트 
		sectionA = str(sectionA)        
		sectionB = str(sectionB)
		sectionC = str(sectionC)
		boxVolume = str(boxVolume)   # 상자 부피
		boxWeight = str(boxWeight)   # 상자무게
		# 현재 상자의 목표구역은 이미 문자형이다
		 
		data = {                               # 변수들의 값을 JSON 형식으로 변환
				"sectionA": sectionA,
				"sectionB": sectionB,
				"sectionC": sectionC,
				"sectionDecision" : sectionDecision,
				"boxVolume": boxVolume,
				"boxWeight" : boxWeight,
				"percentCondition" : percentCondition
				}
				
		# str문자열 형으로 형변환했던 int정수형들을 나중에 연결해 쓰려고 다시 int정수형으로 형변환
		sectionA = int(sectionA)    # 각 구역에 있는 물류의 갯수     
		sectionB = int(sectionB)    
		sectionC = int(sectionC)
		boxVolume = int(boxVolume)   # 상자 부피
		boxWeight = float(boxWeight)   # 상자무게
		percentCondition = int((sectionA + sectionB + sectionC) * 3.33) 


				
		payload = json.dumps(data)  # JSON 객체를 문자열로 인코딩
		mqtt_client.publish(TOPIC, payload, qos=1) # 토픽에 메시지 발행
		time.sleep(1)

		print(">>라즈베리파이에서 aws서버로 데이터 전송이 완료되었습니다<<")
		print("--------------------------------")
