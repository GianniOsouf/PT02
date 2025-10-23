#include <WiFiS3.h>
#include <Stepper.h>

// Wi-Fi
const char ssid[] = "GIANNI";
const char pass[] = "12345678";
WiFiServer server(80);

// Moteur pas à pas
const int stepsPerRevolution = 2048;
Stepper monStepper(stepsPerRevolution, 11, 9, 10, 8);
int currentStep = 0;

// Capteurs
const int trigD = 5;
const int echoD = 6;
const int trigG = 12;
const int echoG = 13;
long distD = 0;
long distG = 0;

// Interrupteurs
const int analogPin = A0;  // switch auto/manuel
const int potPin = A1;     // potentiomètre 3 voies
bool modeAuto = false;

// État
bool engage = false;
int ecart = 20;

void setup() {
  Serial.begin(9600);
  pinMode(trigD, OUTPUT);
  pinMode(echoD, INPUT);
  pinMode(trigG, OUTPUT);
  pinMode(echoG, INPUT);
  monStepper.setSpeed(10);

  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connexion en cours...");
  }

  Serial.print("Adresse IP : ");
  Serial.println(WiFi.localIP());
  server.begin();
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
  modeAuto = (analogRead(analogPin) > 500);
  if (!modeAuto) engage = false;

  // Lecture du potentiomètre en mode manuel
  if (!modeAuto && engage) {
    int potVal = analogRead(potPin);  // plage 0–1023
    int angle = map(potVal, 0, 1023, 0, 180);
    int targetStep = map(angle, 0, 180, 0, stepsPerRevolution);
    int delta = targetStep - currentStep;
    monStepper.step(-delta);
    currentStep = targetStep;
  }

  // Mode auto
  if (modeAuto && engage && distG < ecart && distD < ecart) {
    int delta = distD - distG;
    int angleAuto = constrain(((delta / (float)ecart) * 90) + 90, 0, 180);
    int targetStep = map(angleAuto, 0, 180, 0, stepsPerRevolution);
    int deltaStep = targetStep - currentStep;
    monStepper.step(-deltaStep);
    currentStep = targetStep;
  }

  WiFiClient client = server.available();
  if (client) {
    String req = client.readStringUntil('\r');
    client.flush();

    if (req.indexOf("GET /engage=1") >= 0) engage = true;
    if (req.indexOf("GET /engage=0") >= 0) engage = false;
    if (req.indexOf("GET /ecart=") >= 0) {
      ecart = req.substring(req.indexOf("=") + 1).toInt();
    }

    // Réponse minimale
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/plain");
    client.println();
    client.println("OK");
    client.stop();
  }
}



