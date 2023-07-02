
#include <WiFi.h>
#include <PubSubClient.h>

// Wi-Fi credentials
const char* ssid = "Medialink_1B3A40";
const char* password = "ricenone533";

const char* mqtt_server = "192.168.8.120";
WiFiClient espClient;
PubSubClient client(espClient);

char msg[50];
int value =0;
const char* device_name = "ESP32";

void setup()
{
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void setup_wifi()
{
  Serial.println();
  Serial.print("Connecting to: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  int attempts = 0;
  while(WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    attempts++;
    if(attempts > 3)
    {
      ESP.restart();
    }

    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi Connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* message, unsigned int length)
{
  Serial.print("Message arrived for Topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;

  for(int i=0; i<length; i++)
  {
    Serial.print((char)message[i]);
    messageTemp+= (char)message[i];
  }
  Serial.println();

  /* Put all your message handling here> AKA what you wanna do with a message received or send */

  if(String(topic) == "Test")
  {
    Serial.print("Changing output to ");
    if(messageTemp == "message")
    {
      client.publish("Test", "Message Received from ESP ");
    }
  }

}

void reconnect()
{
  while(!client.connected())
  {
    Serial.print("Attempting MQTT Connect...");

    if(client.connect(device_name))
    {
      Serial.println("Connected");
      client.subscribe("ESPTest");
      client.publish("Test", "Sent from ESP32");
    }
    else
    {
      Serial.print("failed, rc = ");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop()
{
  if(!client.connected())
  {
    reconnect();
  }
  client.loop();
}
// #include <WiFi.h>
// #include <PubSubClient.h>

// // Wi-Fi credentials
// const char* ssid = "Medialink_1B3A40";
// const char* password = "ricenone533";

// // MQTT broker details
// const char* mqttServer = "192.168.8.120";
// const int mqttPort = 1883;
// const char* mqttTopic = "Test";

// WiFiClient espClient;
// PubSubClient client(espClient);

// void setup() {
//   Serial.begin(115200);
//   delay(2000);

//   WiFi.begin(ssid, password);
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(1000);
//     Serial.println("Connecting to WiFi...");
//   }

//   Serial.println("Connected to WiFi");

//   client.setServer(mqttServer, mqttPort);
//   client.setCallback(callback);

//   while (!client.connected()) {
//     if (client.connect(mqttServer)) {
//       Serial.println("Connected to MQTT broker");
//     } else {
//       Serial.print("Failed to connect to MQTT broker, rc=");
//       Serial.print(client.state());
//       Serial.println(" Retrying in 5 seconds...");
//       delay(5000);
//     }
//   }
// }

// void loop() {
//   client.loop();

//   // Publish a message every 5 seconds
//   static unsigned long lastPublishTime = 0;
//   if (millis() - lastPublishTime >= 5000) {
//     publishMessage("Hello from ESP32!");
//     lastPublishTime = millis();
//   }
// }

// void publishMessage(const char* message) {
//   if (client.connected()) {
//     client.publish(mqttTopic, message);
//     Serial.print("Message published: ");
//     Serial.println(message);
//   } else {
//     Serial.println("Failed to publish message. MQTT client not connected.");
//   }
// }

// void callback(char* topic, byte* payload, unsigned int length) {
//   Serial.print("Message received on topic: ");
//   Serial.println(topic);

//   Serial.print("Payload: ");
//   for (int i = 0; i < length; i++) {
//     Serial.print((char)payload[i]);
//   }
//   Serial.println();

//   // Write your code here to handle the received message
// }