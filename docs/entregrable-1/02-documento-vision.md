#  Documento de Visión

## 2.1. Declaración de Visión

> **Para** el personal médico, administrativo y pacientes de la Clínica San Rafael S.A.C.[cite: 1, 3]  
> **Que** enfrentan problemas por la fragmentación de registros clínicos, retrasos en la entrega de resultados y una alta tasa de inasistencia a citas[cite: 1, 3],  
> **El** *Sistema de Información Clínico-Administrativo San Rafael*  
> **Es una** plataforma web integral de gestión médica y administrativa[cite: 1, 3]  
> **Que** unifica la historia clínica electrónica, centraliza la programación de citas con recordatorios automáticos, digitaliza órdenes/resultados de laboratorio y automatiza la facturación con aseguradoras[cite: 1, 3].  
> **A diferencia de** los registros físicos en papel, hojas de cálculo dispersas en Excel y gestión de citas vía telefónica[cite: 1, 3],  
> **Nuestro producto** proporciona acceso en tiempo real a la información clínica con altos estándares de seguridad (Ley N.° 29733), garantizando continuidad en la atención y eficiencia operativa[cite: 1, 3].

---

## 2.2. Perfiles de Usuario (Stakeholders)

| Perfil | Necesidad Principal | Módulo Relacionado |
| :--- | :--- | :--- |
| **Admisión / Recepción** | Agendar, reprogramar y confirmar citas de forma rápida; registrar datos del paciente sin duplicados[cite: 1, 3]. | **M2.** Agenda y citas médicas[cite: 1, 3] |
| **Médico Tratante** | Acceso inmediato a la Historia Clínica Electrónica (HCE) unificada, diagnósticos CIE-10, tratamientos y órdenes de exámenes[cite: 1, 3]. | **M1.** Historia clínica electrónica<br>**M3.** Laboratorio e imágenes[cite: 1, 3] |
| **Enfermera** | Registrar funciones vitales, evoluciones del paciente y verificar indicaciones médicas en atención o emergencia[cite: 1, 3]. | **M1.** Historia clínica electrónica[cite: 1, 3] |
| **Personal de Laboratorio / Imágenes** | Recepcionar órdenes médicas digitales, cargar resultados/informes y notificar al médico tratante[cite: 1, 3]. | **M3.** Laboratorio e imágenes[cite: 1, 3] |
| **Cajero / Facturación** | Generar comprobantes con tarifarios diferenciados (Particular, EPS, SOAT) y gestionar solicitudes de pago / glosas[cite: 1, 3]. | **M4.** Facturación y convenios[cite: 1, 3] |
| **Gerencia Médica** | Visualizar indicadores en tiempo real sobre ocupación de consultorios, tiempos de espera, ingresos e inasistencias[cite: 1, 3]. | **M5.** Reportes gerenciales[cite: 1, 3] |
| **Paciente** | Consultar sus citas programadas, recibir recordatorios y acceder a sus resultados médicos de forma segura[cite: 1, 3]. | **M2.** Agenda y citas médicas<br>**M6.** Portal del paciente[cite: 1, 3] |

---

## 2.3. Análisis de Factibilidad

### 🔹 Factibilidad Técnica
* **Viabilidad:** Alta. Se utilizará un stack de desarrollo moderno y maduro con arquitectura multicapa/microservicios (web + API REST)[cite: 1, 3].
* **Infraestructura:** Despliegue en la nube bajo servicios de costo moderado (PaaS/IaaS), garantizando respuesta menor a 2 segundos en la apertura de historias clínicas sobre un volumen inicial de más de 8,000 pacientes[cite: 1, 3].
* **Seguridad:** Implementación de autenticación basada en roles (RBAC), encriptación de datos sensibles y registros de bitácoras de auditoría no modificables[cite: 1, 3].

### 🔹 Factibilidad Operativa
* **Aceptación:** El sistema responde a la necesidad crítica reportada por la dirección médica respecto a errores de medicación, inasistencias (18%) y demoras de facturación[cite: 1, 3].
* **Usabilidad:** Interfaz minimalista e intuitiva orientada a usuarios con diversos niveles de alfabetización digital[cite: 1, 3].
* **Capacitación:** Se brindarán guías de usuario diferenciadas por rol (Admisión, Médicos, Caja) facilitando la adopción progresiva[cite: 2].

### 🔹 Factibilidad Económica
* **Costo-Beneficio:** El proyecto reduce directamente las pérdidas por glosas no cobradas a las EPS, optimiza los ingresos por ocupación de consultorios y reduce el Ausentismo (*no-show*)[cite: 1, 3].
* **Restricción Presupuestal:** Se alinea a la restricción de infraestructura acotada al utilizar servicios en la nube de nivel de entrada/gratuito durante las fases de desarrollo y prueba[cite: 1, 3].