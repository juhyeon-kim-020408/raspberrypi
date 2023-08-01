import RPi.GPIO as GPIO
import serial
import time

DOUT = 21 # HX711와 라즈베리파이의 핀 번호 설정
SCK = 20
Sigpin = 11 # trm-121a센서 출력핀 할당
Threshold = 0.5 # 감지조건 임계값
MovementCNT = 0 # 움직임 카운트 초기화

# GPIO 모드 설정
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(DOUT, GPIO.IN)
GPIO.setup(SCK, GPIO.OUT)
GPIO.setup(Sigpin, GPIO.IN) # # GPIO 11번 핀을 입력으로 설정

# 라즈베리파이의 uart4와 uart5를 열기
uart4 = serial.Serial("/dev/ttyAMA1", baudrate=9600)
uart5 = serial.Serial("/dev/ttyAMA2", baudrate=9600)

# 거리값을 읽어오는 함수 정의(tof10120센서)
def read_distance(uart):
    # 0x00번지부터 2바이트 읽기
    uart.write(b"\x00\x02")
    data = uart.read(2)
    # 상위 바이트와 하위 바이트를 합치기
    distance = data[0] * 256 + data[1]
    return distance / 100 # cm단위

# HX711에서 데이터를 읽는 함수 정의(로드셀) 
def read_data():
    # 데이터를 저장할 변수 초기화
    data = 0
    
    # DOUT이 LOW가 될 때까지 대기
    while GPIO.input(DOUT) != 0:
        pass
    
    # 24번의 클럭을 발생시키면서 데이터를 읽음
    for i in range(24):
        # SCK를 HIGH로 만듦
        GPIO.output(SCK, 1)
        
        # data에 비트를 추가함
        data = data << 1
        
        # SCK를 LOW로 만듦
        GPIO.output(SCK, 0)
        
        # DOUT이 HIGH면 data에 1을 추가함
        if GPIO.input(DOUT) == 1:
            data = data + 1
    
    # 25번째 클럭으로 gain 값을 설정함 (128로 설정)
    GPIO.output(SCK, 1)
    time.sleep(0.000001)
    GPIO.output(SCK, 0)
    
    # 데이터를 반환함 (2의 보수 형식으로 변환)
    return data ^ 0x800000

# 오프셋 값 설정 (로드셀에 아무것도 올려놓지 않고 측정한 값)
offset = read_data()
# 스케일 값 설정 (로드셀에 알려진 무게를 올려놓고 측정한 값에서 오프셋 값을 뺀 값)
scale = read_data() - offset
# 현재 측정된 값에서 오프셋 값을 뺌(로드셀)
value = read_data() - offset   
# 측정된 값에 스케일 값을 나누어서 무게를 계산함 (로드셀 단위: kg)
weight = value / scale

while True:
	if weight > 0: # 로드셀에서 무게가 감지되면 실행
		print("< 상자가 감지되었습니다!! >")
		Sig = GPIO.input(11) # trm121a센서 11번핀의 상태 읽기
		# tof센서1와 tof센서2에서 거리 데이터 읽기
		distance1 = read_distance(uart4) 
		distance2 = read_distance(uart5) 
    
		# trm121a센서 거리감지
		trmDistance = 0 # trm121a센서 거리값 초기화
		sig = GPIO.input(11) # GPIO 11번 핀에서 신호 읽기
		if sig == 1: # 신호가지 1이면 (물체가 감지되면)
			start = time.time() # 현재 시간을 시작 시간으로 저장
			while GPIO.input(11) == 1: # 신호가 1인 동안
				pass # 아무것도 하지 않음
			end = time.time() # 현재 시간을 종료 시간으로 저장
			duration = end - start # 지속 시간을 계산
			trmDistance = duration * 17150 # 지속 시간에 음속(343 m/s)의 절반을 곱하여 거리를 계산 (단위: cm)

		# trm121a센서 동작감지
		if Sig > Threshold: # 움직임감지 조건
			MovementCNT += 1 # 움직임 카운트 증가
		if MovementCNT > 1: # 움직임이 1번 이상 감지되면
			print("움직임이 감지되었습니다!!!")
			MovementCNT = 0 # 움직임 카운트 초기화
		else: # 움직임이 1번 이상 감지되지 않으면
			print("움직임이 없습니다...")
    

		# 세 거리값(두 개의 tof, 한 개의 trm)의 곱 구하기
		boxVolume = trmDistance * distance1 * distance2

		# 결과 출력하기
		print("trm센서 : %.2f cm" % trmDistance)
		print("tof센서1 : %.2f cm" % distance1)
		print("tof센서2 : %.2f cm" % distance2)
		print("상자의 무게 : %.2f" % weight)
		print("상자 부피 : %.2f cm^3" % boxVolume)
		print("-------------------------")
		# 1초 대기하기
		time.sleep(1)
	else: 
		print("< 상자가 감지되지 않았습니다... >")
		pass
