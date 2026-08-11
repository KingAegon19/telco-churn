# Predicción de churn — Telco

Proyecto de clasificación para identificar clientes en riesgo de cancelar
el servicio, usando el dataset público de Telco Customer Churn de IBM.

## Problema

Los clientes cancelan el servicio y la empresa se entera cuando ya se
fueron. Para entonces no hay margen de acción.

Este proyecto entrena un modelo que identifica qué clientes están en
riesgo de cancelar, antes de que lo hagan.

El área comercial usa esa lista para contactarlos y ofrecer alternativas
de retención. Gerencia la usa para dimensionar el riesgo y asignar
presupuesto.

## Datos

- **Fuente:** [Telco Customer Churn (IBM) — Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
- **Tamaño:** 7.043 clientes, 21 variables
- **Objetivo:** `Churn` (Yes / No)

Descargar el CSV y ubicarlo en `data/raw/`. La carpeta `data/` no está
versionada.

## Estructura

```text
telco-churn/
├── data/
│   ├── raw/                    # datos originales (no versionado)
│   └── processed/              # datos limpios (no versionado)
├── notebooks/
│   ├── 01_exploracion.ipynb    # análisis exploratorio
│   ├── 02_preparacion.ipynb    # limpieza y transformaciones
│   └── 03_modelado.ipynb       # entrenamiento y evaluación
├── requirements.txt
└── README.md
```

## Hallazgos

**El tipo de contrato es el factor más determinante**
- Mes a mes: 42,7% de churn
- Un año: 11,3%
- Dos años: 2,8%

**La fibra óptica duplica el churn frente a DSL**
- Fibra: 41,9% | DSL: 19,0% | Sin internet: 7,4%
- El efecto se mantiene dentro de cada tipo de contrato

**El riesgo se concentra en los primeros meses**
- Antigüedad promedio de quien cancela: 18 meses
- De quien permanece: 37,6 meses

**Perfil crítico:** los clientes con contrato mes a mes y fibra óptica
cancelan en un 54,6% de los casos.

Los clientes que contratan el servicio más costoso sin un compromiso de
permanencia son los que menos duran en la empresa.

## Decisiones tomadas

### Exclusión de clientes sin historia

Once clientes presentaban `TotalCharges` vacío. Todos tenían `tenure = 0`
y `Churn = No`: son clientes recién ingresados que aún no han facturado.
El valor faltante no era un error de captura, sino un evento que no había
ocurrido.

Se excluyeron del análisis porque su condición de "no cancelado" no es
evidencia de permanencia: no han tenido oportunidad de irse. Representan
el 0,15% del total.

### Unificación de etiquetas redundantes

Siete columnas incluían los valores "No internet service" o "No phone
service", que duplican información ya contenida en `InternetService` y
`PhoneService`. Se unificaron con "No" para reducir dimensionalidad sin
pérdida de información: la distinción sigue siendo reconstruible cruzando
ambas columnas.

### Eliminación de TotalCharges

`TotalCharges` es esencialmente el producto de `tenure` y `MonthlyCharges`,
por lo que no aporta información nueva.

En el modelo inicial su coeficiente resultó positivo (+0,56), lo que
contradice la lógica del negocio: un cliente con mayor facturación
acumulada lleva más tiempo y debería tener menor riesgo. Ese signo
inesperado es señal de multicolinealidad.

Se entrenó sin la variable y el recall pasó de 0,80 a 0,79, sin pérdida
material. El coeficiente de `tenure` se estabilizó de −1,22 a −0,77,
confirmando que estaba distorsionado.

**Decisión:** se elimina. Se gana estabilidad e interpretabilidad sin
costo en desempeño.

### Feature de interacción: creada y descartada

El análisis exploratorio sugirió una interacción entre contrato mes a mes
y fibra óptica. Se construyó una variable binaria para capturarla, ya que
la regresión logística no detecta interacciones por sí sola.

Al evaluarla, su coeficiente resultó negativo (−0,40) y al eliminarla el
recall pasó de 0,79 a 0,78. La interacción no aportaba: el efecto
combinado ya estaba capturado por las variables individuales.

**Decisión:** se descarta. El análisis bivariado exageraba el efecto al
no controlar por las demás variables.

### Métrica objetivo: recall

El 73,4% de los clientes permanece, de modo que un modelo que prediga
"nadie cancela" acertaría el 73,4% de las veces y sería inútil: no
marcaría a nadie para contactar. Esa es la línea base a superar.

El costo de los dos errores no es simétrico. No detectar a un cliente que
cancela significa perderlo. Contactar a uno que iba a quedarse cuesta una
llamada. Por eso se prioriza recall sobre precisión.

Se usó `class_weight='balanced'` para evitar que el modelo optimice
exactitud apostando a la clase mayoritaria.

### Modelo final: regresión logística

Se compararon regresión logística y Random Forest mediante validación
cruzada de cinco particiones sobre el conjunto de entrenamiento.

- Regresión logística: recall promedio 0,795
- Random Forest: recall promedio 0,773

El modelo más complejo no superó a la línea base y mostró mayor dispersión
entre particiones.

A igual desempeño se prefiere la logística por interpretabilidad: sus
coeficientes indican dirección y magnitud del efecto de cada variable. El
Random Forest solo reporta importancia relativa, sin señalar si una
variable aumenta o reduce el riesgo, lo que limita su utilidad para
orientar acciones de retención.

## Resultados

Evaluación sobre el conjunto de prueba (1.407 clientes, no vistos durante
el entrenamiento):

| Métrica | Valor |
|---|---|
| Recall (clase churn) | 0,79 |
| Precisión | 0,49 |
| F1 | 0,61 |
| Exactitud | 0,73 |
| Línea base | 0,734 |

Validación cruzada sobre entrenamiento: recall promedio 0,795, con rango
entre 0,72 y 0,84 según la partición.

**Lectura operativa:** de 1.407 clientes, el modelo marca 610. De esos,
300 cancelaban efectivamente y 310 se habrían quedado. Quedan 74 clientes
sin detectar.

### Variables más relevantes

| Variable | Coeficiente | Efecto |
|---|---|---|
| InternetService_No | −1,16 | protege |
| InternetService_Fiber optic | +1,01 | aumenta riesgo |
| Contract_Two year | −0,91 | protege |
| tenure | −0,77 | protege |
| Contract_Month-to-month | +0,74 | aumenta riesgo |

### Entregable

Una lista de clientes ordenada por probabilidad de cancelación, para que
el área comercial priorice el contacto. El umbral de corte se ajusta según
la capacidad operativa del equipo: bajarlo amplía la cobertura a costa de
más falsas alarmas.

## Limitaciones

**El modelo identifica riesgo, no certeza**
Entrega una probabilidad de cancelación, no una predicción definitiva. Un
cliente marcado puede permanecer, y uno no marcado puede irse.

**No explica las causas**
El análisis muestra que los clientes de fibra óptica cancelan más, pero no
permite determinar por qué. Podría relacionarse con calidad del servicio,
relación precio-valor, o el perfil de cliente que contrata ese producto.
Distinguirlo requeriría datos de reclamos, incidencias técnicas o
encuestas de salida.

**La efectividad de la intervención no está verificada**
El proyecto asume que contactar a un cliente en riesgo aumenta la
probabilidad de retenerlo. Ese supuesto no se probó. Validarlo requeriría
un grupo de control: contactar a una parte de los clientes marcados y
comparar resultados.

**Los datos son una fotografía, no un histórico**
Cada cliente aparece con su estado en un momento único. No hay información
sobre fallas del servicio, reclamos ni evolución del consumo. Con datos
históricos por cliente sería posible detectar señales tempranas de
inconformidad que hoy no son visibles.

**Costo operativo de las falsas alarmas**
Con precisión de 0,49, aproximadamente la mitad de los clientes
contactados se habrían quedado sin intervención.

## Cómo reproducirlo

```powershell
git clone https://github.com/KingAegon19/telco-churn.git
cd telco-churn

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Descargar el dataset de Kaggle a `data/raw/` y ejecutar los notebooks en
orden numérico.