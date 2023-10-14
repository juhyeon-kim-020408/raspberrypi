
#[1초동안 10 개의 거리값을 측정하고 그들의 평균값을 출력해주는 코드]
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO 
import time, json, ssl, sys, serial

GPIO.setwarnings(False) 




# 라즈베리파이의 uart2, 3, 4, 5 시리얼포트 열기
uart2 = serial.Serial("/dev/ttyAMA1", baudrate=9600)     # 상부센서
uart3 = serial.Serial("/dev/ttyAMA2", baudrate=9600)     # 측면센서
uart4 = serial.Serial("/dev/ttyAMA3", baudrate=9600)     # 측면센서
uart5 = serial.Serial("/dev/ttyAMA4", baudrate=9600)     # 후방센서(tof10120)

a = 38    # 로드셀부터 상부센서까지의 거리
b = 14.5    # 측센서부터 로드셀 중앙까지의 거리리
c = 11   # 후방센서부터 로드셀 중앙까지의 거리 


while True:
	
	 # 거리값을 저장할 리스트 생성(초기화)
	distances1 = []
	distances2 = []
	distances3 = []
	distances4 = []
	station = ""   # 구역 문자열 초기화
	
	# n번 반복하면서 센서로부터 데이터 읽기
	for i in range(10):
		data1 = uart2.readline().decode().strip()
		data2 = uart3.readline().decode().strip()
		data3 = uart4.readline().decode().strip()
		data4 = uart5.readline().decode().strip()
		
		# 데이터를 정수로 변환하여 거리 값으로 처리
		distance1 = a - int(data1) 
		distance2 = b - int(data2)
		distance3 = b - int(data3)
		distance4 = c - int(data4[0:-2])/10
		# 거리값을 리스트에 추가
		distances1.append(distance1)
		distances2.append(distance2)
		distances3.append(distance3)
		distances4.append(distance4)
			
		time.sleep(0.001)
	print("측정완료")
	# n개의 거리값의 평균 계산
	distanceAverage1 = sum(distances1) / 10
	distanceAverage2 = sum(distances2) / 10
	distanceAverage3 = sum(distances3) / 10
	distanceAverage4 = sum(distances4) / 5
	
	boxVolume = int(distanceAverage1 * (distanceAverage2 + distanceAverage3) * distanceAverage4)
	
	# 평균값 출력
	print("1 : %.2f" % distanceAverage1)
	print("2 : %.2f" % distanceAverage2)
	print("3 : %.2f" % distanceAverage3)
	print("4 : %.2f" % distanceAverage4)
	print("상자 부피 : %.2fcm" % boxVolume)


	print("==================================")
	# 1초에 한 번 평균값 출력
	time.sleep(0.01)
	