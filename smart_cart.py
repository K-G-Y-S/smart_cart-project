from __future__ import print_function
from selenium import webdriver
from time import sleep
import heapq
import re
import serial
import time
import json

try:
	import cv2
	from ar_markers import detect_markers
except ImportError:
	raise Exception('Error: OpenCv is not installed')

zone_id = 1

drv = webdriver.Chrome(executable_path="/home/pi/chromedriver")


#arduino = serial.Serial('/dev/ttyUSB0',9600)

def sendposition(var):
	var = var.encode('utf-8')
	arduino.write(var)
	time.sleep(1)

def dijkstra(graph, start, end):
	distances = {vertex : [float('inf'), start] for vertex in graph}
	distances[start] = [0, start]
	queue = []
	heapq.heappush(queue, [distances[start][0], start])

	while queue:
		current_distance, current_vertex = heapq.heappop(queue)
 
		if distances[current_vertex][0] < current_distance:
			continue
		for adjacent, weight in graph[current_vertex].items():
			distance = current_distance + weight

			if distance < distances[adjacent][0]:
				distances[adjacent] = [distance, current_vertex]
				heapq.heappush(queue, [distance, adjacent])

	path = end
	path_output = end + '->'
 
	while distances[path][1] != start:
		path_output += distances[path][1] + '->'
		path = distances[path][1]

	path_output += start
	print(path_output)
	route =path_output.replace('->','')
	print(route)

	numlist = re.findall(r'\d+', path_output)
	numlist = [int(i) for i in numlist]
	print(numlist)

	a = len(numlist)
	print(a)

	rowlist = [ 16, 12, 8, 4]
	state = 0
	rowState = 0
	
	for i in range(a):
		path_send = numlist[i]
		for j in rowlist:
			if path_send < j+1:
				row = j/4
		print(row)

		if i == 0 : 
			row_pre = row
			num_pre = path_send
			continue
		if row > row_pre:
			rowState = 0
			if state > 0:
				for i in range(state):
					position = 'l'
					print(position)
					sendposition(position)
					state = state - 1
			if state < 0:
				for i in range(abs(state)):
					position = 'r'
					print(position)
					sendposition(position)
					state = state + 1
			position = 'f'
			
		elif row < row_pre:
			rowState = 0
			position = 'b'
		elif row == row_pre:
			
			if path_send > num_pre:
				if rowState == 0:
					position = 'r'
					state = state + 1
					print(position)
					sendposition(position)
					rowState = 1
				
				position = 'f'
			else :
				if rowState == 0:
					position = 'l'
					state = state - 1
					print(position)
					sendposition(position)
					rowState = 1
					
				position = 'f'

		row_pre = row
		num_pre = path_send
		print(position)
		sendposition(position)
		time.sleep(1)
		position = 's'
		sendposition(position)

		path_pre = path_send

	return distances

mygraph = {
	'1' : {'2' : 1, '5' : 1},
	'2'  : {'1' : 1, '3': 1, '6': 1},
	'3'  : {'2' : 1, '4' : 1, '7' : 1},
	'4'  : {'3' : 1, '8' : 1},
	'5'  : {'1' : 1, '6' : 1, '9' : 1},
	'6'  : {'2' : 1, '5' : 1, '7' : 1, '10' : 1},
	'7'  : {'3' : 1, '6' : 1, '8' : 1, '11' : 1},
	'8'  : {'4' : 1, '7' : 1, '12' : 1},
	'9'  : {'5' : 1, '10' : 1, '13' : 1},
	'10' : {'6' : 1, '9' : 1, '11' : 1, '14' : 1},
	'11' : {'7' : 1, '10' : 1, '12' : 1, '15' : 1},
	'12' : {'8' : 1, '11' : 1, '16' : 1},
	'13' : {'9' : 1, '14' : 1},
	'14' : {'10' : 1,'13' : 1, '15' : 1},
	'15' : {'11' : 1, '14' : 1, '16'},
	'16' : {'12' : 1, '15' : 1},
	
}

if __name__ == '__main__':
    drv.get('http://localhost:8080')
    capture = cv2.VideoCapture(0)
    sleep(3)
    print('Press "q" to quit')
    
    if capture.isOpened():  # try to get the first frame
        frame_captured, frame = capture.read()
    else:
        frame_captured = False
    while frame_captured:
        markers = detect_markers(frame)
        marker_id = "0"
        print(markers)
        for marker in markers:
            marker.highlite_marker(frame)
            marker_id = marker.comeon_id(frame)
        cv2.imshow('Test Frame',frame)
        if id == "1":
            position = ''
            print(position)
            sendposition(position)
        position = 'f'

        #start_point = str(input('start point : '))
        #end_point = str(input('end point : '))
        #dijkstra(mygraph, end_point, start_point)
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        frame_captured, frame = capture.read()

        drv.execute_script("update_id(%s)" %(marker_id))
        
