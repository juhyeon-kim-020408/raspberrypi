import serial
import time

# 라즈베리파이의 uart4와 uart5를 열기
uart4 = serial.Serial("/dev/ttyAMA1", baudrate=9600)
uart5 = serial.Serial("/dev/ttyAMA2", baudrate=9600)

# 센서에서 거리 데이터를 읽는 함수
def read_distance(uart):
    # 0x00번지부터 2바이트 읽기
    uart.write(b"\x00\x02")
    data = uart.read(2)
    # 상위 바이트와 하위 바이트를 합치기
    distance = data[0] * 256 + data[1]
    return distance

while True:
    # 센서1과 센서2에서 거리 데이터 읽기
    distance1 = read_distance(uart4)
    distance2 = read_distance(uart5)
    # 거리 데이터 곱하기
    product = distance1 * distance2
    # 결과 출력하기
    print("Distance1: %d mm" % distance1)
    print("Distance2: %d mm" % distance2)
    print(f"Product: {product} mm^2")
    print("----------")
    # 1초 대기하기
    time.sleep(1)
    