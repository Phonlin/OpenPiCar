OpenPiCar
====
Raspberry Pi 執行 OpenCV，應用 Arduino Nano 之純視覺自駕車

OpenPiCar.py 執行在 Raspberry Pi 之 Python 3.8 環境

run.ino 為 Arduino IDE 程式，可執行於 Arduino 開發版

![](./example/Drive.gif)

[完整影片](https://drive.google.com/file/d/17_OAvOQTvfPxzX3tlLnaojhIOwBYyfLx/view?usp=drive_link)

OpenPiCar.py
----
`影像邊緣檢測`：使用Canny邊緣檢測器處理影像，提取出影像中的邊緣

`區域遮罩提取`：定義一個三角形區域，將影像中的非感興趣區域遮罩掉，只保留車道區域

`霍夫變換檢測直線`：使用霍夫變換檢測車道中的直線

`顯示檢測到的直線`：將檢測到的直線畫在原始影像上

`計算平滑車道線`：將霍夫變換檢測到的直線進行平滑，分別計算左車道和右車道的斜率和截距

`計算車道偏移和方向`：根據車道線的斜率和截距計算車道偏移，使用 PySerial 初始化串口通信傳至 Arduino

`顯示車道線和影像融合`：將平滑後的車道線畫在影像上，並將融合後的影像顯示

按下鍵盤上的 'q' 鍵結束程式

run.ino
----
`輸出腳位定義`：定義四個馬達的控制腳位 rf、rb、lf、lb 分別代表右前、右後、左前、左後

`輸入字串及轉換`：使用 Serial.readStringUntil('\n') 讀取從串口接收的字串，並轉換成浮點數 (float)

`根據數值控制馬達`：根據接收到的浮點數值 s2f 進行條件判斷，決定馬達的轉速

`馬達控制`：
* 使用 analogWrite 函數控制馬達的轉速，根據不同的條件設定 lf、rf、lb、rb 的 PWM 值
* 如果數值為負值，表示需要向左轉，根據數值的大小設定左輪 lf 和右輪 rf 的轉速，其他輪子停止
* 如果數值為正值，表示需要向右轉，根據數值的大小設定左輪 lf 和右輪 rf 的轉速，其他輪子停止
