#include <Servo.h>

Servo monServo;

const int trigD = 5;
const int echoD = 6;
const int trigG = 10;
const int echoG = 11;
const int servoPin = 3;

long distD = 0;
long distG = 0;

void setup() {
  Serial.begin(9600);
  monServo.attach(servoPin);
  pinMode(trigD, OUTPUT);
  pinMode(echoD, INPUT);
  pinMode(trigG, OUTPUT);
  pinMode(echoG, INPUT);
}

long lireDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH, 30000);
  return duration * 0.034 / 2;
}

void loop() {
  distD = lireDistance(trigD, echoD);
  distG = lireDistance(trigG, echoG);

  Serial.print("G:");
  Serial.print(distG);
  Serial.print(";D:");
  Serial.println(distD);

  delay(200);

  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    int angle = input.toInt();
    if (angle >= 0 && angle <= 180) {
      monServo.write(angle);
    }
  }
}
