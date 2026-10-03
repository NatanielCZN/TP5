"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 2: El Problema del Oso y las Abejas
Bibliografía de Referencia:
- Silberschatz: Cap. 6.6 (Problemas clásicos de sincronización)
- Stallings: Cap. 5.4 (Sincronización con semáforos)
"""

import sys
import threading
import time
import random

# Configuración UTF-8 para consola Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

M = 10                  # Capacidad del tarro de miel
NUM_ABEJAS = 5          # Número de abejas obreras
tarro_miel = 0          # Variable compartida
simulacion_activa = True

# TODO PARA EL ESTUDIANTE:
# 1. Define los mecanismos de sincronización necesarios:
# - Un cerrojo (Lock) o semáforo binario para exclusión mutua en el tarro.
# - Un semáforo para despertar al oso cuando el tarro esté lleno.
# - Un semáforo para que las abejas esperen si el tarro está lleno o el oso está comiendo.
mutex = threading.Lock()
sem_oso = threading.Semaphore(0)
sem_tarro_disponible = threading.Semaphore(1)


def abeja(id_abeja):
    global tarro_miel, simulacion_activa
    while simulacion_activa:
        time.sleep(random.uniform(0.05, 0.2))

        # Esperar hasta que el tarro esté libre para poner miel.
        sem_tarro_disponible.acquire()

        # Acceso exclusivo al tarro.
        mutex.acquire()
        try:
            if tarro_miel < M:
                tarro_miel += 1
                print(f"[Abeja {id_abeja}] deposita miel -> tarro: {tarro_miel}/{M}")

                # Si el tarro se llena, despertamos al oso.
                if tarro_miel == M:
                    print(f"[Abeja {id_abeja}] Tarro lleno. Despertando al oso.")
                    sem_oso.release()
            else:
                # Si por algún motivo el tarro ya estaba lleno, lo devolvemos a la cola.
                sem_tarro_disponible.release()
        finally:
            mutex.release()

        # Si el tarro no está lleno, otras abejas pueden seguir produciendo.
        # Si está lleno, no se libera el semáforo; el oso lo vaciará y luego hará release().
        if tarro_miel < M:
            sem_tarro_disponible.release()


def oso(max_tarros=2):
    global tarro_miel, simulacion_activa
    tarros_comidos = 0
    while tarros_comidos < max_tarros and simulacion_activa:
        # =====================================================================
        # TODO PARA EL ESTUDIANTE:
        # 1. Esperar pasivamente (bloqueado) hasta que una abeja señale que el tarro está lleno:
        #    sem_oso.acquire()
        # 2. Comerse toda la miel (tarro_miel = 0).
        # 3. Incrementar tarros_comidos += 1.
        # 4. Avisar a las abejas que el tarro está vacío y disponible (sem_tarro_disponible.release()).
        # =====================================================================
        sem_oso.acquire()

        mutex.acquire()
        try:
            print(f"[Oso] Comiendo el tarro completo. Miel anterior: {tarro_miel}/{M}")
            tarro_miel = 0
            print(f"[Oso] Tarro vaciado. Ahora queda: {tarro_miel}/{M}")
        finally:
            mutex.release()

        tarros_comidos += 1
        print(f"[Oso] Tarro #{tarros_comidos} consumido.")

        # Avisamos que el tarro ya quedó vacío y otra abeja puede seguir trabajando.
        sem_tarro_disponible.release()

    simulacion_activa = False


if __name__ == "__main__":
    print("=" * 60)
    print(" Iniciando Simulación: El Oso y las Abejas (UNJu FI)")
    print("=" * 60)

    # Crear e iniciar los hilos para el oso y las N abejas.
    hilos = []
    for i in range(NUM_ABEJAS):
        t = threading.Thread(target=abeja, args=(i + 1,), daemon=True)
        hilos.append(t)
        t.start()

    t_oso = threading.Thread(target=oso, args=(2,), daemon=True)
    t_oso.start()

    for hilo in hilos:
        hilo.join()
    t_oso.join()

    print("\nSimulación finalizada.")

