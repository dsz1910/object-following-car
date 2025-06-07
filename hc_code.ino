#define centreTrig 2
#define centreEcho 3
#define leftTrig 8
#define leftEcho 9


float getDistance(int trig, int echo) {
  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);

  long duration = pulseIn(echo, HIGH);
  float distance = duration * 0.0343 / 2;
  return distance;
}

void setup() {
  pinMode(centreEcho, INPUT);
  pinMode(centreTrig, OUTPUT);
  pinMode(leftTrig, OUTPUT);
  pinMode(leftEcho, INPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();
    float distance = -1.0;

    if (cmd == 'C') {
      distance = getDistance(centreTrig, centreEcho);
    }
    else if (cmd == 'L') {
      distance = getDistance(leftTrig, leftEcho);
    }
    
    if (distance >= 0) {
      Serial.println(distance);
    }
    else {
      Serial.println("err");
    }
  }

}

