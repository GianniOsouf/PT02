#include <Stepper.h>

const int stepsPerRevolution = 2048;
Stepper monStepper(stepsPerRevolution, 8, 10, 9, 11); // IN1 à IN4 sur ULN2003

const int trigD = 5;
const int echoD = 6;
const int trigG = 12;
const int echoG = 13;

long distD = 0;
long distG = 0;

int currentStep = 0; // position actuelle en pas

void setup() {
  Serial.begin(9600);
  pinMode(trigD, OUTPUT);
  pinMode(echoD, INPUT);
  pinMode(trigG, OUTPUT);
  pinMode(echoG, INPUT);
  monStepper.setSpeed(10); // RPM
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
      int targetStep = map(angle, 0, 180, 0, stepsPerRevolution); // conversion angle → pas
      int delta = targetStep - currentStep;
      monStepper.step(-delta);
      currentStep = targetStep;
    }
  }
}
