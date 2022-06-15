#define ledPin 12
int state = 0;

void setup() {
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);
  Serial.begin(9600); // Default communication rate of the Bluetooth module
}

void loop() {
  if(Serial.available() > 0){ // Checks whether data is comming from the serial port
    state = Serial.read(); // Reads the data from the serial port
    Serial.println(state);
 }

 if (state == 48) {
  digitalWrite(ledPin, LOW); // Turn LED OFF
  state = 48;
 }
 else if (state == 49) {
  digitalWrite(ledPin, HIGH);
  state = 49;
 } 
}
