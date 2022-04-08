import cv2
import numpy as np
import serial
import math

COM_PORT = '/dev/ttyUSB0'
BAUD_RATES = 9600
ser = serial.Serial(COM_PORT, BAUD_RATES)


def canyEdgeDetector(image):
    edged = cv2.Canny(image, 50, 150)

    return edged


def getROI(image):
    height, width = image.shape

    triangle = np.array(
        [[(0, height), (width, height), (width, int(height * 0.55)),
          (0, int(height * 0.55))]])

    black_image = np.zeros_like(image)
    block = cv2.fillPoly(black_image, triangle, (255, 255, 255))
    masked_total = cv2.bitwise_and(image, block)

    return masked_total


def getLines(image):
    lines = cv2.HoughLinesP(image, 1, np.pi / 180, 80, np.array([]), minLineLength=50, maxLineGap=10)

    return lines


def displayLines(image, lines):
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line
            cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 10)

    return image


def getLineCoordinatesFromParameters(image, line_parameters):
    height, width, _ = image.shape
    slope = line_parameters[0]
    intercept = line_parameters[1]
    y1 = height
    y2 = int(y1 * (1 / 2))

    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))

    return [x1, y1, x2, y2]


def getSmoothLines(image, lines):
    lane_lines = []
    if lines is None:
        return lane_lines

    height, width, _ = image.shape
    left_fit = []
    right_fit = []

    boundary = 1 / 3
    left_region_boundary = width * (1 - boundary)
    right_region_boundary = width * boundary

    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        if x1 == x2:
            continue
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        slope = parameters[0]
        intercept = parameters[1]

        if slope < 0:
            if x1 < left_region_boundary and x2 < left_region_boundary:
                left_fit.append((slope, intercept))
        if slope > 0:
            if x1 > right_region_boundary and x2 > right_region_boundary:
                right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(getLineCoordinatesFromParameters(image, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(getLineCoordinatesFromParameters(image, right_fit_average))

    return lane_lines


def getmind(image, lines):
    global x_offset
    height, width, _ = image.shape
    if len(lines) == 0:
        return lines

    if len(lines) == 1:
        x1, _, x2, _ = lines[0]
        x_offset = x2 - x1

    else:
        _, _, left_x2, _ = lines[0]
        _, _, right_x2, _ = lines[1]
        camera_mid_offset_percent = 0.00
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(x_offset / y_offset)

    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)
    steering_angle = angle_to_mid_deg + 0
    print(angle_to_mid_radian)

    # 傳送偏移率給pyserial
    str2bytes = str(int(angle_to_mid_radian * 100)).encode()
    ser.write(bytes(str2bytes))
    ser.write(b'\n')

    while ser.in_waiting:
        mcu_feedback = ser.readline().decode()  # 接收回應訊息並解碼
        print('控制板回應：', mcu_feedback)

    return angle_to_mid_radian


def displaymind(image, smooth_lines):
    height, width, _ = image.shape
    if smooth_lines == []:
        return smooth_lines
    if len(smooth_lines) == 1:
        for line in smooth_lines:
            x1, y1, x2, y2 = line
            a = int(width/2)
            b = int(height)
            c = int(int(width/2)-(x1-x2))
            d = int(height/2)
            cv2.line(image, (a, b), (c, d), (255, 0, 0), 10)

    else:
        x1, _, x2, _ = smooth_lines[0]
        x3, _, x4, _ = smooth_lines[1]
        cv2.line(image, (int((x3+x1)/2), int(height)), (int((x2+x4)/2), int(height/2)), (255, 0, 0), 10)


videoFeed = cv2.VideoCapture(0)

while True:
        (status, image) = videoFeed.read()
        copy = np.copy(image)

        edged_image = canyEdgeDetector(image)
        roi_image = getROI(edged_image)

        lines = getLines(roi_image)

        smooth_lines = getSmoothLines(image, lines)

        mind = getmind(image, smooth_lines)
        displaymind(image, smooth_lines)

        image_with_smooth_lines = displayLines(image, smooth_lines)
        transparent = cv2.addWeighted(copy, 0.5, image_with_smooth_lines, 0.5, 0)

        cv2.imshow("Output", transparent)
        if cv2.waitKey(10) == ord('q'):
            break