#include "Arduino.h"
#include "math.h"

//1 tour =16*200
struct motor_struc {
  //k corespond a une constante qui harmonise le nombre de tick pour degres pour chaque moteur de sorte a ce que ki*tcki soit tous egaux
  int pin_dir, pin_step, pwm_channel;
  int long tck, last_tck, I_tck, e, last_e, i_e, d_e, v;
  double freq, ki = 0, kp = 0, kd = 0;
};


motor_struc motor[2];


void pin_definition() {
  motor[0].pin_step = 14;
  motor[0].pin_dir = 13;
  motor[1].pin_step = 26;
  motor[1].pin_dir = 27;


  motor[0].pwm_channel = 5;
  motor[1].pwm_channel = 3;
}


void pin_setup() {
  for (int i = 0; i < 3; i++) {
    pinMode(motor[i].pin_step, OUTPUT);
    pinMode(motor[i].pin_dir, OUTPUT);
    ledcSetup(motor[i].pwm_channel, 10, 8);
    ledcAttachPin(motor[i].pin_step, motor[i].pwm_channel);
    ledcWrite(motor[i].pwm_channel, 0);
  }
}

void moteurstep(int nb, int frequence) {
  ledcSetup(motor[nb].pwm_channel, frequence, 8);
}

void moteurstep_power(int nb, bool power, bool sens) {
  digitalWrite(motor[nb].pin_dir, sens);
  if(power){
  ledcWrite(motor[nb].pwm_channel, 150);

  }else{
  ledcWrite(motor[nb].pwm_channel, 0);
  digitalWrite(motor[nb].pin_step, LOW);

  }
}

void setup() {

  xTaskCreatePinnedToCore(
    tread2,    // Pointeur vers la fonction de la tâche
    "tread2",  // ²Nom de la tâche
    10000,     // Taille de la pile de la tâche
    NULL,      // Paramètre de la tâche
    1,         // Priorité de la tâche
    NULL,      // Pointeur vers la tâche
    1          // Numéro du cœur (0 pour le premier cœur, 1 pour le deuxième)
  );

  // put your setup code here, to run once:
  Serial.begin(115200);  // console / uart0
  delay(1000);
  setCpuFrequencyMhz(240);
  pin_definition();
  pin_setup();
  Serial.println(getCpuFrequencyMhz());
}

void tread2(void *parameter) {
  while (1) {
    if (Serial.available() > 0) {
      char commande = Serial.read();  // Lit la commande envoyée par l'utilisateur

      // Condition pour chaque caractère envoyé
      if (commande == 'd') {
        moteurstep(1, 650);
        moteurstep_power(1, true, false);
        delay(50);
        moteurstep_power(1, true, false);
        // Action pour la commande aller a droite
      } else if (commande == 'g') {
        moteurstep(0, 650);
        delay(50);
        moteurstep_power(1, true, true);
        delay(50);
        moteurstep_power(1, true, true);
        // Action pour la1commande aller a gauche
      } else if (commande == 'h') {
        //m0 sens true 1000
        // Action pour la commande aller haut
        moteurstep(0, 450);
        delay(50);
        moteurstep_power(0, true, true);
        delay(50);
        moteurstep_power(0, true, true);
      } else if (commande == 'b') {
        // Action pour la commande aller bas
        //m0 sens false 1000
        moteurstep(0, 450);
        delay(50);
        moteurstep_power(0, true, false);
        delay(50);
        moteurstep_power(0, true, false);
      } else if (commande == 'v') {
        // Action pour stop m0
        moteurstep_power(0, false, false);
        moteurstep_power(0, false, false);
        moteurstep_power(0, false, false);
        digitalWrite(motor[0].pin_step, LOW);
      } else if (commande == 'r') {
        // Action pour stop m1
        moteurstep_power(1, false, false);
        delay(50);
        moteurstep_power(1, false, false);
      }


    } else {
    }
  }
}

void loop() {

}



/*
a expliquer ,
en vrai self explain donc juste a lire

*/
