int rf = 3;
int rb = 5;
int lf = 11;
int lb = 10;

String str;

void setup() {
  pinMode(3, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if(Serial.available()) {
    str = Serial.readStringUntil('\n');
    int s2f = str.toFloat();
    if (s2f < 0) {
      if (s2f < -50){
        analogWrite(lf, 20);
        analogWrite(rf, 130-s2f);
        analogWrite(lb, 0);
        analogWrite(rb, 0);
        }
      else {
      analogWrite(lf, 50);
      analogWrite(rf, 50-s2f);
      analogWrite(lb, 0);
      analogWrite(rb, 0);
            }
    }
    else if (s2f > 0) {
      if (s2f > 50){
        analogWrite(lf, 130+s2f);
        analogWrite(rf, 40);
        analogWrite(lb, 0);
        analogWrite(rb, 0);
        }
      else {
      analogWrite(lf, 50+s2f);
      analogWrite(rf, 50);
      analogWrite(lb, 0);
      analogWrite(rb, 0);
            }
      }
  }
}
