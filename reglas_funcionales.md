# Economy RP - Documento de Requisitos y Reglas Funcionales

> **Documento fuente:** `requeriments.pdf` (Versión 1)  
> **Institución:** Institución Universitaria Pascual Bravo – Ingeniería de Software I / Bases de Datos I  
> **Equipo de Trabajo (Grupo 4):**  
> - Miguel Ángel Cardona Agudelo  
> - Luisa María López Orrego  
> - Jorge Luis Ordoñez Ávila  
> **Asesor:** Juan Camilo Palacio Alcaraz  

---

## 1. Visión General del Negocio y Objetivos

### 1.1 Descripción del Negocio
Motor de gestión económica centralizado en una base de datos relacional para servidores privados de rol GTA (FiveM, RedM, RAGE MP, Grand RP). Su propósito es reemplazar scripts independientes sin comunicación por un sistema unificado que registre jugadores, empleos, bienes y transacciones, garantizando trazabilidad completa y previniendo fraudes, duplicaciones e hiperinflación.

### 1.2 Objetivos del Sistema
- **Seguridad y Verificabilidad:** Convertir el tradeo P2P en una operación segura donde ninguna parte sufra incumplimientos a mitad del proceso.
- **Control Económico:** Frenar la hiperinflación y el desbalance provocado por tradeos descontrolados y duplicación de ítems.
- **Erradicación de Mercado Ilícito:** Eliminar bienes duplicados o de procedencia ilegítima.
- **Protección Patrimonial:** Evitar que los tradeos queden truncados por caídas de red o desconexiones intencionadas/accidentales.
- **Eficiencia Operativa:** Reducir tiempos y costos de soporte técnico/moderación ante disputas de jugadores mediante un historial técnico inmutable.

---

## 2. Actores y Roles

| Actor / Rol | Descripción y Responsabilidades Funcionales |
|---|---|
| **Jugador** | Usuario del servidor de rol. Administra su cuenta bancaria y su inventario de bienes. Puede ofrecer, aceptar o rechazar propuestas de intercambio/tradeo con otros jugadores. Realiza jornadas laborales. |
| **Jugador Comerciante** | Jugador que vende vehículos o propiedades a otros dentro de la trama de rol (gestión de concesionarios o bienes raíces), inyectando bienes al mercado. |
| **Moderador de Economía** | Encargado de revisar reportes de jugadores sobre tradeos fallidos, bienes con restricciones ocultas o intentos de fraude. Escala incidentes graves al administrador. |
| **Administrador del Servidor** | Configura parámetros económicos globales (salarios, precios base, límites de bienes, tasas de comisión, tiempos de enfriamiento). Interviene en fraudes y consulta auditorías/historiales de transacciones. |

---

## 3. Catálogo Oficial de Reglas de Negocio (RN)

| Código | Nombre | Descripción | Fórmula / Condición Lógica | Fuente | Reglas Relacionadas |
|---|---|---|---|---|---|
| **RN001** | **Registro único laboral** | Cuando un jugador completa un empleo dentro del servidor, el sistema debe calcular y acreditar automáticamente la ganancia correspondiente a su cuenta, dejando registro de la fecha y el empleo que la generó. | $$\text{Ganancia} = \text{Tarifa\_base\_empleo} \times \text{Horas\_trabajadas}$$ | Equipo de desarrollo | RN003, RN005 |
| **RN002** | **Propiedad Única y Exclusiva** | Un bien físico específico (un vehículo con una placa determinada, una casa en una dirección exacta) solo puede pertenecer a un (1) personaje a la vez. | $(\text{Propietario}) = 1 \text{ para cada } \text{\$Bien\_id} \text{ activo}$ | Lógica de bienes raíces y vehículos | RN003, RN004 |
| **RN003** | **Inmutabilidad del Historial** | Una vez que una transacción (compra, venta, transferencia, pago de salario) es registrada en el sistema, no puede ser modificada, editada ni eliminada bajo ninguna circunstancia. | Política de base de datos (Append-only / Logs inmutables) | Auditoría y Seguridad | RN001, RN002, RN004, RN005 |
| **RN004** | **Restricción de transferencia por deuda** | Un bien no puede transferirse ni revenderse a otro jugador si tiene una deuda o una cuota pendiente asociada (ej. un vehículo financiado que aún no ha sido pagado en su totalidad) o estado de embargo. | $\text{Restriccion} = \text{'Ninguna'}$ (No transferible si $\text{Restriccion} \in \{\text{'Deuda Pendiente'}, \text{'Embargado'}\}$) | Equipo de desarrollo | RN002, RN003 |
| **RN005** | **Trazabilidad de Creación de Dinero** | Todo dinero inyectado a la economía que no provenga de otro jugador (ej. pago de salarios, bonos iniciales) debe tener como cuenta de origen la cuenta oficial del "Sistema" del servidor. | $\text{Origen} = \text{'Cuenta\_Sistema'} \text{ si } \text{Emisor} = \text{Sistema/No-Personaje}$ | Equipo de desarrollo | RN001, RN003 |
| **RN006** | **Comisión por Transferencia** | Toda compraventa o intercambio entre jugadores debe descontar un porcentaje fijo del monto transferido como comisión, que se acredita a la cuenta del "Sistema" y no a ningún jugador, funcionando como mecanismo de drenaje (money sink) anti-inflación. | $$\text{Comision} = \text{Monto\_transaccion} \times \text{Porcentaje\_comision}$$ | Equipo de desarrollo | RN001, RN005 |
| **RN007** | **Límite Máximo de Propiedades** | Un jugador no puede tener registrados a su nombre más vehículos o propiedades del límite que defina el administrador del servidor, para evitar acaparamiento y desbalance de oferta. | $$\text{Cantidad\_bienes}(\text{Jugador}) \le \text{Limite\_definido}$$ | Administrador del servidor | RN002 |
| **RN008** | **Periodo de Enfriamiento Laboral** | Un jugador debe esperar un tiempo mínimo definido por el servidor entre el final de una jornada laboral y el inicio de la siguiente en ese mismo empleo, evitando explotación continua de ganancias. | $$\text{Hora\_actual} - \text{Hora\_ultima\_jornada} \ge \text{Tiempo\_enfriamiento}$$ | Equipo de desarrollo | RN001 |
| **RN009** | **Penalización por Bancarrota** | Si el saldo de un jugador queda en negativo o no alcanza a cubrir sus deudas pendientes, el sistema lo declara en bancarrota, congela temporalmente su capacidad de realizar transacciones y le aplica una penalización económica definida por el administrador antes de rehabilitarlo. | $\text{Saldo\_disponible} < 0 \implies \text{Estado} = \text{'BANCARROTA'}$ (Operaciones bloqueadas) | Administrador del servidor | RN003, RN009 |
| **RN010** | **Confirmación Doble en el Tradeo** | Todo tradeo debe ser confirmado explícitamente por ambos jugadores involucrados sobre los términos finales (bien y dinero ofrecidos) antes de ejecutar la transferencia. Si alguno modifica los términos luego de haber confirmado el otro, la confirmación se reinicia inmediatamente. | $\text{Ejecutar si } (\text{confirmacion\_j1} = \text{true} \land \text{confirmacion\_j2} = \text{true})$ | Equipo de desarrollo | RN003, RN013 (RN012) |
| **RN011** | **Límite Diario de Tradeos** | Un jugador no puede ejecutar más de 5 tradeos dentro de un mismo día calendario, previniendo lavado de activos o transferencias masivas repetitivas. | $$\text{Tradeos\_del\_dia}(\text{Jugador}) \le 5$$ | Administrador del servidor | RN006 |
| **RN012** | **Tradeo Único Simultáneo** | Un jugador solo puede tener abierta una única negociación de tradeo a la vez. Mientras esté pendiente de confirmación, no puede iniciar ni aceptar ninguna otra propuesta, impidiendo comprometer el mismo bien o saldo en operaciones paralelas. | $\text{Negociaciones\_activas}(\text{Jugador}) \le 1$ | Equipo de desarrollo | RN002, RN011 |

---

## 4. Reglas Funcionales de Procesos y Operaciones del Sistema

### 4.1 Proceso de Tradeo P2P (Intercambio entre Jugadores)
1. **Atomicidad de la Transacción:**
   - Toda transferencia de dinero y traspaso de propiedad debe realizarse bajo una única transacción ACID atómica.
   - Si ocurre un fallo de red o cancelación, el estado debe revertirse completamente (`ROLLBACK`), impidiendo pérdidas o duplicaciones de ítems.
2. **Validaciones Previas Obligatorias:**
   - **Verificación de Propiedad:** Validar en base de datos en tiempo real que el ítem pertenezca efectivamente al emisor (`T_Item.id_jugador == emisor`).
   - **Verificación de Gravámenes:** Comprobar que el ítem a intercambiar no tenga deudas ni esté embargado (`T_Item.restriccion == 'Ninguna'`).
   - **Verificación de Fondos:** Validar que el comprador tenga saldo suficiente (`saldo_disponible >= monto_ofrecido + comision`).
   - **Verificación de Límites:** Validar que el receptor no supere el límite máximo de bienes permitidos (`RN007`) ni el cupo diario de 5 tradeos (`RN011`).
   - **Exclusividad de Sesión:** Verificar que ninguno de los participantes tenga otra negociación abierta (`RN012`).
3. **Mecanismo de Doble Aceptación:**
   - Cualquier alteración en los montos o ítems resetea automáticamente las banderas `confirmacion_j1` y `confirmacion_j2` a `false`.
   - La ejecución solo ocurre cuando `confirmacion_j1 == true` y `confirmacion_j2 == true`.
4. **Deducción de Comisión (Drenaje):**
   - Se deduce automáticamente la comisión parametrizada en el servidor y se acredita a la cuenta `SISTEMA_EMISOR`. El monto restante se abona al vendedor.

### 4.2 Proceso Laboral y Emisión de Salarios
1. **Validación Server-Side:**
   - La liquidación de jornadas y acreditación de dinero debe ser calculada y validada estrictamente por el servidor contra la base de datos, prohibiendo la alteración de montos desde la memoria del cliente.
2. **Registro Histórico de la Jornada:**
   - Cada jornada completada genera un registro inmutable en `T_Jornada_Laboral` con `horas_trabajadas`, `fecha_hora` y `monto_pagado` (para cumplimiento de 3FN).
3. **Control de Cooldown (Enfriamiento):**
   - El sistema debe verificar que hayan transcurrido al menos `tiempo_enfriamiento_min` minutos desde la última jornada antes de permitir una nueva en el mismo empleo.
4. **Inyección Controlada:**
   - El pago de salario se registra como una transacción formal vinculada a `T_Jornada_Laboral`, donde el emisor contable es la cuenta oficial del Sistema (`RN005`).

### 4.3 Proceso Contable, Auditoría y Bitácora
1. **Partida Doble Desglosada:**
   - Toda transacción se descompone en un encabezado general (`T_Transaccion`) y sus respectivos asientos contables en `T_Detalle_Transaccion` indicando:
     - Cuenta Origen (`cuenta_origen`)
     - Cuenta Destino (`cuenta_destino`)
     - Monto parcial (`monto_detalle`)
     - Concepto explícito (ej. `'PAGADO_A_VENDEDOR'`, `'COMISION_DRENAJE_SISTEMA'`, `'PAGO_SALARIO'`).
2. **Inalterabilidad de Registros:**
   - Prohibición de sentencias `UPDATE` o `DELETE` sobre las tablas `T_Transaccion` y `T_Detalle_Transaccion`.
   - Cualquier rectificación administrativa debe realizarse mediante una nueva transacción de compensación o reversión (`estado_transaccion = 'REVERTIDA'`).
3. **Trazabilidad de Bienes:**
   - El campo `T_Item.antiguedad_dias` se registra como valor numérico para permitir el cálculo dinámico de depreciación sin almacenar redundancias temporales.

---

## 5. Modelo Lógico Relacional (Esquema y Atributos)

### 5.1 Definición de Tablas y Restricciones

```
                    ┌─────────────────────────┐
                    │       T_Servidor        │
                    ├─────────────────────────┤
                    │ id_servidor (PK)        │
                    │ nombre                  │
                    │ porcentaje_comision     │
                    │ limite_bienes_por_jugador
                    │ tiempo_enfriamiento_min │
                    └───────────┬─────────────┘
                                │ 1:N
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
┌─────────────────────────┐                   ┌─────────────────────────┐
│        T_Empleo         │                   │        T_Jugador        │
├─────────────────────────┤                   ├─────────────────────────┤
│ id_empleo (PK)          │                   │ id_jugador (PK)         │
│ id_servidor (FK)        │                   │ id_servidor (FK)        │
│ nombre_empleo           │                   │ credenciales            │
│ tarifa_base             │                   │ estado                  │
└───────────┬─────────────┘                   └───────────┬─────────────┘
            │ 1:N                                         │ 1:1 (opcional Sist.)
            ▼                                             ▼
┌─────────────────────────┐                   ┌─────────────────────────┐
│    T_Jornada_Laboral    │◄──────────────────┤        T_Cuenta         │
├─────────────────────────┤   (1:N por Jug)   ├─────────────────────────┤
│ id_jornada (PK)         │                   │ id_cuenta (PK)          │
│ id_jugador (FK)         │                   │ id_jugador (FK, Unique) │
│ id_empleo (FK)          │                   │ tipo_cuenta             │
│ horas_trabajadas        │                   │ saldo_inicial           │
│ fecha_hora              │                   │ saldo_disponible        │
│ ganancia_calculada /    │                   └───────────┬─────────────┘
│ monto_pagado            │                               │
└───────────┬─────────────┘                               │ 1:N (Origen/Destino)
            │                                             ▼
            │ 1:1 (opc.)                      ┌─────────────────────────┐
            └────────────────┐                │  T_Detalle_Transaccion  │
                             ▼                ├─────────────────────────┤
                    ┌─────────────────────────┤ id_detalle (PK)         │
                    │      T_Transaccion      │ id_transaccion (FK)     │
                    ├─────────────────────────┤ cuenta_origen (FK)      │
                    │ id_transaccion (PK)     │ cuenta_destino (FK)     │
                    │ id_item_afectado (FK)   │ monto_detalle           │
                    │ id_negociacion (FK)     │ concepto                │
                    │ id_jornada (FK)         │└─────────────────────────┘
                    │ tipo_transaccion        │
                    │ estado_transaccion      │
                    │ monto                   │
                    │ fecha_hora              │
                    └───────────▲─────────────┘
                                │
            ┌───────────────────┴──────────────────┐
            │ 1:1 (opc.)                           │ 1:1 (opc.)
            ▼                                      ▼
┌─────────────────────────┐              ┌─────────────────────────┐
│  T_Negociacion_Tradeo   │              │         T_Item          │
├─────────────────────────┤              ├─────────────────────────┤
│ id_negociacion (PK)     │              │ id_item (PK)            │
│ id_jugador_1 (FK)       │              │ id_jugador (FK)         │
│ id_jugador_2 (FK)       │              │ nombre                  │
│ id_item_ofrecido (FK)   │              │ precio                  │
│ monto_ofrecido          │              │ fecha                   │
│ confirmacion_j1         │              │ restriccion             │
│ confirmacion_j2         │              │ antiguedad_dias         │
│ estado                  │              └─────────────────────────┘
│ fecha_creacion          │
└─────────────────────────┘
```

### 5.2 Estructura DBML Oficial del Sistema

```dbml
Table T_Servidor {
  id_servidor int [pk]
  nombre varchar
  porcentaje_comision decimal
  limite_bienes_por_jugador int
  tiempo_enfriamiento_min int
}

Table T_Jugador {
  id_jugador int [pk]
  id_servidor int [ref: > T_Servidor.id_servidor]
  credenciales varchar
  estado varchar // 'ACTIVO', 'BANCARROTA', 'SUSPENDIDO'
}

Table T_Empleo {
  id_empleo int [pk]
  id_servidor int [ref: > T_Servidor.id_servidor]
  nombre_empleo varchar
  tarifa_base decimal
}

Table T_Jornada_Laboral {
  id_jornada int [pk]
  id_jugador int [ref: > T_Jugador.id_jugador]
  id_empleo int [ref: > T_Empleo.id_empleo]
  horas_trabajadas decimal
  fecha_hora timestamp
  ganancia_calculada decimal // Almacenado como monto_pagado inmutable
}

Table T_Cuenta {
  id_cuenta int [pk]
  id_jugador int [unique, ref: > T_Jugador.id_jugador] // 1 a 1, NULL para cuenta Sistema
  tipo_cuenta varchar // 'PERSONAL', 'SISTEMA_EMISOR'
  saldo_inicial decimal
  saldo_disponible decimal
}

Table T_Item {
  id_item int [pk]
  id_jugador int [ref: > T_Jugador.id_jugador]
  nombre varchar
  precio decimal
  fecha timestamp
  restriccion varchar // 'Ninguna', 'Embargado', 'Deuda Pendiente'
  antiguedad_dias int
}

Table T_Negociacion_Tradeo {
  id_negociacion int [pk]
  id_jugador_1 int [ref: > T_Jugador.id_jugador]
  id_jugador_2 int [ref: > T_Jugador.id_jugador]
  id_item_ofrecido int [ref: > T_Item.id_item]
  monto_ofrecido decimal
  confirmacion_j1 boolean
  confirmacion_j2 boolean
  estado varchar // 'PENDIENTE', 'CONFIRMADO', 'CANCELADO'
  fecha_creacion timestamp
}

Table T_Transaccion {
  id_transaccion int [pk]
  id_item_afectado int [ref: > T_Item.id_item]
  id_negociacion int [ref: > T_Negociacion_Tradeo.id_negociacion]
  id_jornada int [ref: > T_Jornada_Laboral.id_jornada]
  tipo_transaccion varchar // 'PAGO_SALARIO', 'TRADEO_P2P', 'COMPRA_COMERCIANTE'
  estado_transaccion varchar // 'COMPLETADA', 'CANCELADA', 'REVERTIDA'
  monto decimal
  fecha_hora timestamp
}

Table T_Detalle_Transaccion {
  id_detalle int [pk]
  id_transaccion int [ref: > T_Transaccion.id_transaccion]
  cuenta_origen int [ref: > T_Cuenta.id_cuenta]
  cuenta_destino int [ref: > T_Cuenta.id_cuenta]
  monto_detalle decimal
  concepto varchar // 'PAGADO_A_VENDEDOR', 'COMISION_DRENAJE_SISTEMA'
}
```

---

## 6. Enlaces y Recursos del Proyecto
- **Diagrama Conceptual (Draw.io):** [Ver en Diagrams.net](https://app.diagrams.net/#G1vccAkyamnuTZAjezohfrKgFDja_E1Yg4#%7B%22pageId%22%3A%22DgIu1eW9WFayZ3NLflwW%22%7D) | [Ver en Google Drive](https://drive.google.com/file/d/1vccAkyamnuTZAjezohfrKgFDja_E1Yg4/view?usp=sharing)
- **Diagrama Lógico (DBDiagram):** [https://dbdiagram.io/d/6aa9e23baf7c3b0bd1e995fe](https://dbdiagram.io/d/6aa9e23baf7c3b0bd1e995fe)
