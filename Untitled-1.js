import processing.serial.*;

Serial arduino;
String portName = "COM3"; // à adapter selon ton système
String seuilInput = "";
boolean engagement = false;
String message = "";
String distG = "";
String distD = "";
String servoPos = "";

void setup() {
  size(400, 300);
  arduino = new Serial(this, portName, 9600);
  arduino.bufferUntil('\n');
  textFont(createFont("Arial", 14));
}

void draw() {
  background(240);
  
  fill(0);
  text("Saisir seuil (cm) :", 20, 30);
  rect(150, 10, 100, 25);
  fill(255);
  rect(151, 11, 98, 23);
  fill(0);
  text(seuilInput, 155, 30);
  
  fill(engagement ? color(0, 200, 0) : color(200, 0, 0));
  rect(270, 10, 100, 25);
  fill(255);
  text(engagement ? "Désengager" : "Engager", 280, 30);
  
  fill(0);
  text("Distance Gauche : " + distG + " cm", 20, 80);
  text("Distance Droite : " + distD + " cm", 20, 110);
  text("Servo : " + servoPos, 20, 140);
  text(message, 20, 180);
}

void keyPressed() {
  if (key == '\n' || key == '\r') {
    if (seuilInput.length() > 0) {
      arduino.write("SEUIL=" + seuilInput + "\n");
      seuilInput = "";
    }
  } else if (key == BACKSPACE && seuilInput.length() > 0) {
    seuilInput = seuilInput.substring(0, seuilInput.length()-1);
  } else if (key >= '0' && key <= '9') {
    seuilInput += key;
  }
}

void mousePressed() {
  if (mouseX > 270 && mouseX < 370 && mouseY > 10 && mouseY < 35) {
    engagement = !engagement;
    arduino.write("ENGAGER\n");
  }
}

void serialEvent(Serial p) {
  String line = p.readStringUntil('\n');
  line = trim(line);
  
  if (line.startsWith("Gauche:")) {
    String[] parts = split(line, '|');
    distG = parts[0].replace("Gauche:", "").trim();
    distD = parts[1].replace("Droite:", "").trim();
  } else if (line.startsWith("🔄 Servo")) {
    servoPos = line.substring(2);
  } else if (line.startsWith("⚠️") || line.startsWith("⛔") || line.startsWith("✅") || line.startsWith("➡️")) {
    message = line;
  }
}
