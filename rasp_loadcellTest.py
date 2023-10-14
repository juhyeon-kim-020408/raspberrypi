import RPi.GPIO as GPIO
import time
import sys
GPIO.setwarnings(False)
EMULATE_HX711=False

referenceUnit = -469.004
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
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()

print("로드셀 준비 완료!")
time.sleep(0.5)

while True:
	
	weightList = []
	while True:                     # 로드셀 위에 물체가 올라가야 다음단계를 실행시키는 반복문
		val = hx.get_weight(1) 
		if val > 0:
			break
		else:
			pass
	hx.power_down()
	hx.power_up()
	while True:
		val = hx.get_weight(1)
		if val > 100:              
			pass
		else:
			break
		#print(val)
		hx.power_down()
		hx.power_up()
		for i in range(10):
			# 로드셀 무게측정
			weight = hx.get_weight(1)
			weightList.append(weight) # 리스트에 추가
			
			time.sleep(0.1)
		hx.power_down()
		hx.power_up()
		weightAverage = sum(weightList) / len(weightList) # 로드셀 평균 구하기
		print("무게 : %.2f" % weightAverage)
		print("--------------")

