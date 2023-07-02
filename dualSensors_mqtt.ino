#include <WiFi.h>
#include <PubSubClient.h>
#include "Adafruit_VL53L0X.h"

// Wi-Fi credentials
//const char* ssid = "Medialink_1B3A40";
//const char* password = "ricenone533";
const char* ssid = "Jarvis";
const char* password = "javinpinko";
// MQTT broker
//const char* mqttServer = "192.168.8.120"; //Pi IP
const char* mqttServer = "192.168.56.1";  //laptop IP
const int mqttPort = 1883;
const char* mqttTopic = "Shot Status";

// address we will assign if dual sensor is present
#define LOX1_ADDRESS 0x30
#define LOX2_ADDRESS 0x31

// set the pins to shutdown
#define SHT_LOX1 16
#define SHT_LOX2 17

// objects for the vl53l0x
Adafruit_VL53L0X lox1 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox2 = Adafruit_VL53L0X();

// this holds the measurement
VL53L0X_RangingMeasurementData_t measure1;
VL53L0X_RangingMeasurementData_t measure2;

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Received message on topic: ");
  Serial.println(topic);
  Serial.print("Message: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
      client.subscribe(mqttTopic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void setID() {
  // all reset
  digitalWrite(SHT_LOX1, LOW);    
  digitalWrite(SHT_LOX2, LOW);
  delay(10);
  // all unreset
  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, HIGH);
  delay(10);

  // activating LOX1 and resetting LOX2
  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, LOW);

  // initing LOX1
  if (!lox1.begin(LOX1_ADDRESS)) {
    Serial.println(F("Failed to boot first VL53L0X"));
    while (1);
  }
  delay(10);

  // activating LOX2
  digitalWrite(SHT_LOX2, HIGH);
  delay(10);

  //initing LOX2
  if (!lox2.begin(LOX2_ADDRESS)) {
    Serial.println(F("Failed to boot second VL53L0X"));
    while (1);
  }
}

void read_dual_sensors() {
  lox1.rangingTest(&measure1, false);
  lox2.rangingTest(&measure2, false);
  //int correct_order[] = { 5, 5 };
  int correct_order[] = {0,0}; //0 can equal idle/untriggered

  //begin eval for order of sensors triggering
  Serial.print(F("1: "));
  if (measure1.RangeStatus != 4) {
    Serial.print(measure1.RangeMilliMeter);
    if (measure1.RangeMilliMeter < 120) {
      correct_order[0] = 1; //1 can equal triggered
    }
  } /*else {
    Serial.print(F("Out of range"));
  }*/
  delay(100);

  //Serial.print(F(" "));
  Serial.print(F(" 2: "));
  if (measure2.RangeStatus != 4) {
    Serial.print(measure2.RangeMilliMeter);
    if (measure2.RangeMilliMeter < 160) {
      correct_order[1] = 1;
    }
  } /*else {
    Serial.print(F("Out of range"));
  }*/

  //ADD LOGIC TO ACCOUNT FOR MISSES RN THERES ONLY LOGIC TO ACCOUNT FOR MAKES
  /* Could look like this for 1 scenerion of misses: Only bottom sensor triggered
    //Would have make several condition checks for other miss cases
    if (measure2.RangeMilliMeter < 100) { //in this case only the bottom sensor was triggered
      if(correct_order[0] == 5) //if the first sensor was never changed from 5 aka never triggered
      {
        correct_order[1] = 3; //so then you could check for combination of correct_order={5,3}
      }
      correct_order[1] = 2;
    }
  */
  Serial.println();
  //if (correct_order == {0,0}): means no triggers & no signal sent out

  //if(correct_order == {1,0}): means only first sensor was triggered: send out "Miss" signal
  if (correct_order[0] == 1 && correct_order[1] == 0) {
    Serial.println("Only Rim Triggered: Miss");

    // Publish MQTT message
    if (client.connected()) {
      client.publish(mqttTopic, "Only Rim Triggered: Miss");
      Serial.println("Message published to MQTT broker");
    }
  }

  //if(correct_order == {0,1}): means only 2nd sensor triggered: send out "Miss" signal
  if (correct_order[0] == 0 && correct_order[1] == 1) {
    Serial.println("Only Net Triggered: Miss");

    // Publish MQTT message
    if (client.connected()) {
      client.publish(mqttTopic, "Only Net Triggered: Miss");
      Serial.println("Message published to MQTT broker");
    }
  }

  //if(correct_order == {1,1}): means both triggered: send out "Make" signal 
  if (correct_order[0] == 1 && correct_order[1] == 1) {
    Serial.println("Sensors Triggered in Correct Order");

    // Publish MQTT message
    if (client.connected()) {
      client.publish(mqttTopic, "Sensors Triggered in Correct Order");
      Serial.println("Message published to MQTT broker");
    }
  }
  correct_order[0] = 0;
  correct_order[1] = 0;

  delay(500);
}

void setup() {
  Serial.begin(115200);

  // Wait until serial port opens for native USB devices
  while (!Serial) { delay(1); }

  pinMode(SHT_LOX1, OUTPUT);
  pinMode(SHT_LOX2, OUTPUT);

  Serial.println(F("Shutdown pins inited..."));

  digitalWrite(SHT_LOX1, LOW);
  digitalWrite(SHT_LOX2, LOW);

  Serial.println(F("Both in reset mode...(pins are low)"));

  Serial.println(F("Starting..."));
  setID();

  setup_wifi();
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  read_dual_sensors();
  delay(100);
}
