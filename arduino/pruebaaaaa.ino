#include "R200.h"
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

BLEServer *pServer = NULL;
BLECharacteristic *pTxCharacteristic;
bool deviceConnected = false;

#define SERVICE_UUID           "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID_RX "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID_TX "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

unsigned long lastResetTime = 0;
R200 rfid;
uint8_t team_uid[60][12] = {0};
String lastRxData = "";
int zumbador = 0;
String modo = "BUS";  // "BUS" o "SEG"
const int MAX_UIDS = 60;
int missingCounts[MAX_UIDS] = {0};
const int MISSING_THRESHOLD = 5;


void BLEBegin();
void AddTag();
bool informationUID();
void ShowTeamUID();
bool isTagStored(uint8_t* uid);
void SendDataToPhone(int index);
void AddTeamUID();
void checkStoredTagInRange();

class MyServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    Serial.println("Bluetooth connected");
    deviceConnected = true;
  }

  void onDisconnect(BLEServer* pServer) {
    Serial.println("Bluetooth disconnected");
    deviceConnected = false;
    delay(500);
    pServer->startAdvertising();
  }
};

class MyCallbacks: public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) {
    String rxValue = pCharacteristic->getValue();

    Serial.println("*********");
    Serial.print("Mensaje recibido: ");
    Serial.println(rxValue);
    Serial.println("*********");

    if (rxValue == "LEER_ETIQUETA") {
      AddTag();
    } 
    else if (rxValue.startsWith("team_uid:")) {
      lastRxData = rxValue.substring(9);
      AddTeamUID();
    } 
    else if (rxValue.startsWith("MODE:")) {
      String newMode = rxValue.substring(5);
      if (newMode == "BUS" || newMode == "SEG") {
        modo = newMode;
        Serial.print("🔄 Modo cambiado a: ");
        Serial.println(modo);
      } else {
        Serial.println("⚠️  Modo no reconocido.");
      }
    }
    else if (rxValue.startsWith("ADD:") || rxValue.startsWith("DEL:") || rxValue.startsWith("UPDATE:")) {
      String command = rxValue.substring(0, rxValue.indexOf(':'));
      String hexUid = rxValue.substring(rxValue.indexOf(':') + 1);
      Serial.print("Comando recibido: ");
      Serial.println(command);
      Serial.print("UUID recibido: ");
      Serial.println(hexUid);

      uint8_t parsedUid[12] = {0};
      int byteIndex = 0;
      char hexBuffer[hexUid.length() + 1];
      hexUid.toCharArray(hexBuffer, sizeof(hexBuffer));
      char *token = strtok(hexBuffer, ":");

      while (token != NULL && byteIndex < 12) {
        parsedUid[byteIndex++] = strtol(token, NULL, 16);
        token = strtok(NULL, ":");
      }

      if (byteIndex != 12) {
        Serial.println("❌ UID no tiene 12 bytes válidos.");
        return;
      }

      if (command == "ADD") {
        if (isTagStored(parsedUid)) {
          Serial.println("Etiqueta ya almacenada");
          return;
        }
        for (int i = 0; i < 60; i++) {
          bool empty = true;
          for (int j = 0; j < 12; j++) {
            if (team_uid[i][j] != 0) {
              empty = false;
              break;
            }
          }
          if (empty) {
            memcpy(team_uid[i], parsedUid, 12);
            Serial.print("✅ UUID almacenado en posición ");
            Serial.println(i);
            ShowTeamUID();
            return;
          }
        }
        Serial.println("❌ Memoria llena, no se pudo guardar más etiquetas.");
      }

      else if (command == "DEL") {
        for (int i = 0; i < 60; i++) {
          if (memcmp(team_uid[i], parsedUid, 12) == 0) {
            memset(team_uid[i], 0, 12);
            Serial.print("🗑️  Etiqueta eliminada en posición ");
            Serial.println(i);
            ShowTeamUID();
            return;
          }
        }
        Serial.println("⚠️  Etiqueta no encontrada para eliminar.");
      }

      else if (command == "UPDATE") {
        bool found = false;
        for (int i = 0; i < 60; i++) {
          if (memcmp(team_uid[i], parsedUid, 12) == 0) {
            memset(team_uid[i], 0, 12);
            Serial.print("🔁 Etiqueta eliminada (UPDATE) en posición ");
            Serial.println(i);
            ShowTeamUID();
            found = true;
            break;
          }
        }

        if (!found) {
          for (int i = 0; i < 60; i++) {
            bool empty = true;
            for (int j = 0; j < 12; j++) {
              if (team_uid[i][j] != 0) {
                empty = false;
                break;
              }
            }
            if (empty) {
              memcpy(team_uid[i], parsedUid, 12);
              Serial.print("✅ Etiqueta añadida (UPDATE) en posición ");
              Serial.println(i);
              ShowTeamUID();
              return;
            }
          }
          Serial.println("❌ Memoria llena, no se pudo añadir la etiqueta (UPDATE).");
        }
      }
    }

  }
};

void setup() {
  Serial.begin(9600);
  Serial.println(__FILE__ __DATE__);

  rfid.begin(&Serial1, 115200, 20, 21);
  rfid.dumpModuleInfo();
  rfid.gainTransmissionMax();
  rfid.gainReceptorMax();
  BLEBegin();

  memset(team_uid, 0, sizeof(team_uid));
}

void loop() {
  if (modo == "BUS") {
    checkStoredTagInRange();
  } else if (modo == "SEG") {
    seguimientoEtiquetas();
  }
}

void BLEBegin() {
  BLEDevice::init("Lossn't");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);

  pTxCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID_TX,
    BLECharacteristic::PROPERTY_NOTIFY
  );
  pTxCharacteristic->addDescriptor(new BLE2902());

  BLECharacteristic *pRxCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID_RX,
    BLECharacteristic::PROPERTY_WRITE
  );
  pRxCharacteristic->setCallbacks(new MyCallbacks());

  pService->start();
  pServer->getAdvertising()->start();
  Serial.println("Esperando conexión...");
}

void AddTag() {
  unsigned long startTime = millis();
  while (millis() - startTime < 5000) {
    rfid.loop();
    if (millis() - lastResetTime > 60) {
      rfid.poll();
      lastResetTime = millis();
    }
    if (informationUID()) break;
    delay(60);
  }

  if (!informationUID()) return;

  if (isTagStored(rfid.uid)) {
    Serial.println("Etiqueta ya almacenada");
    ShowTeamUID();
    return;
  }

  for (int i = 0; i < 60; i++) {
    bool empty = true;
    for (int j = 0; j < 12; j++) {
      if (team_uid[i][j] != 0) {
        empty = false;
        break;
      }
    }
    if (empty) {
      memcpy(team_uid[i], rfid.uid, 12);
      Serial.print("Etiqueta añadida en posición ");
      Serial.println(i);
      ShowTeamUID();
      SendDataToPhone(i);
      delay(1000);
      return;
    }
  }

  Serial.println("No hay espacio disponible para una nueva etiqueta.");
}

bool informationUID() {
  for (int j = 0; j < 12; j++) {
    if (rfid.uid[j] != 0) return true;
  }
  return false;
}

bool isTagStored(uint8_t* uid) {
  for (int i = 0; i < 60; i++) {
    if (memcmp(team_uid[i], uid, 12) == 0) return true;
  }
  return false;
}

void ShowTeamUID() {
  for (int i = 0; i < 60; i++) {
    Serial.print("Etiqueta ");
    Serial.print(i);
    Serial.print(": ");
    for (int j = 0; j < 12; j++) {
      char hexStr[4];
      sprintf(hexStr, "%02X", team_uid[i][j]);
      Serial.print(hexStr);
      if (j < 11) Serial.print(":");
    }
    Serial.println();
  }
}

void SendDataToPhone(int index) {
  if (!deviceConnected || index < 0 || index >= 60) return;

  String tagData = "";
  for (int j = 0; j < 12; j++) {
    char hexStr[4];
    sprintf(hexStr, "%02X", team_uid[index][j]);
    tagData += hexStr;
    if (j < 11) tagData += ":";
  }

  pTxCharacteristic->setValue(tagData.c_str());
  pTxCharacteristic->notify();
  Serial.println("Etiqueta enviada al móvil: " + tagData);
}

void AddTeamUID() {
  Serial.println("Procesando datos para team_uid...");
  Serial.println("Raw data: " + lastRxData);
  
  int row = 0;
  char buffer[lastRxData.length() + 1];
  lastRxData.toCharArray(buffer, sizeof(buffer));
  char *token = strtok(buffer, ",");

  while (token != NULL && row < 60) {
    if (strlen(token) != 24) {
      Serial.print("Formato incorrecto: ");
      Serial.println(token);
      token = strtok(NULL, ",");
      continue;
    }

    for (int i = 0; i < 12; i ++) {
      char byteStr[3] = {token[i*2], token[i*2+1], '\0'};
      team_uid[row][i] = strtol(byteStr, NULL, 16);
    }

    Serial.print("Etiqueta ");
    Serial.print(row);
    Serial.print(": ");
    for (int j = 0; j < 12; j++) {
      char hexStr[4];
      sprintf(hexStr, "%02X", team_uid[row][j]);
      Serial.print(hexStr);
      if (j < 11) Serial.print(":");
    }
    Serial.println();

    row++;
    token = strtok(NULL, ",");
  }

  Serial.print("Total de etiquetas cargadas: ");
  Serial.println(row);
}
void printUID(uint8_t* uid, int len = 12) {
  for (int i = 0; i < len; i++) {
    Serial.print(uid[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
}
void clearUID() {
  for (int i = 0; i < 12; i++) {
    rfid.uid[i] = 0;
  }
}

void checkStoredTagInRange() {
  rfid.loop();

  if (millis() - lastResetTime > 60) {
    rfid.poll();
    lastResetTime = millis();
  }

  if (!informationUID()) return;
  Serial.print("UID leído: ");
  printUID(rfid.uid);

  if (isTagStored(rfid.uid)) {
    Serial.println("✅ ¡Etiqueta conocida detectada!");
    // pinMode(zumbador, OUTPUT);
    // digitalWrite(zumbador, HIGH);
    // delay(200);
    // digitalWrite(zumbador, LOW);
    // pinMode(zumbador, INPUT);
    for (int i = 0; i < 60; i++) {
      if (memcmp(team_uid[i], rfid.uid, 12) == 0) {
        SendDataToPhone(i);
        break;
      }
    }
    delay(2000); // evitar spam
    clearUID();
  }
  else{
    Serial.println("❌ ¡Etiqueta desconocida!");
    delay(2000);
    clearUID();
  }
}

void seguimientoEtiquetas() {
  static bool etiquetasDetectadas[MAX_UIDS] = {false};
  memset(etiquetasDetectadas, 0, sizeof(etiquetasDetectadas));

  rfid.loop();
  if (millis() - lastResetTime > 60) {
    rfid.poll();
    lastResetTime = millis();
  }

  if (informationUID()) {
    for (int i = 0; i < MAX_UIDS; i++) {
      if (memcmp(team_uid[i], rfid.uid, 12) == 0) {
        etiquetasDetectadas[i] = true;
        missingCounts[i] = 0;
        break;
      }
    }
  }

  for (int i = 0; i < MAX_UIDS; i++) {
    if (team_uid[i][0] != 0) { // hay etiqueta válida
      if (!etiquetasDetectadas[i]) {
        missingCounts[i]++;
        if (missingCounts[i] % MISSING_THRESHOLD == 0) {
          // Alcanza el umbral: notificar
          SendDataToPhone(i); // Se puede usar esto para notificar etiqueta perdida
          Serial.print("⚠️  ¡Etiqueta perdida! UID: ");
          for (int j = 0; j < 12; j++) {
            Serial.printf("%02X", team_uid[i][j]);
            if (j < 11) Serial.print(":");
          }
          Serial.println();
        }
      } else {
        missingCounts[i] = 0; // Reset si fue detectada
      }
    }
  }

  clearUID();
  delay(500);
}

