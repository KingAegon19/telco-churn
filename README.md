# Predicción de churn — Telco

Proyecto de clasificación para identificar clientes en riesgo de cancelar el servicio (churn), usando el dataset público de Telco Customer Churn de IBM.

## Datos

- **Fuente:** [Telco Customer Churn (IBM) — Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
- **Tamaño:** 7.043 clientes, 21 variables
- **Target:** `Churn` (Yes / No)

Descarga el CSV desde Kaggle y colócalo en `data/raw/`. La carpeta `data/` no está versionada en git (ver `.gitignore`).

## Estructura del proyecto

```text
telco-churn/
├── data/
│   ├── raw/            # datos originales, sin modificar (no versionado)
│   └── processed/      # datos limpios/transformados (no versionado)
├── notebooks/
│   └── 01_exploracion.ipynb   # análisis exploratorio (EDA)
├── src/
│   ├── config.py        # rutas y constantes del proyecto
│   └── data.py           # carga y limpieza de datos
├── requirements.txt
└── README.md
```

Los notebooks van numerados en el orden en que se ejecutan (`01_`, `02_`, ...) y se apoyan en funciones reutilizables definidas en `src/` para evitar duplicar lógica.

## Cómo correrlo en otra PC

```powershell
git clone https://github.com/<tu-usuario>/telco-churn.git
cd telco-churn

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Luego descarga el CSV del dataset y colócalo en `data/raw/`, y abre `notebooks/01_exploracion.ipynb` con Jupyter/VS Code.

## Estado del proyecto

- [x] Estructura base del repo
- [x] Carga y limpieza inicial de datos (`src/data.py`)
- [ ] Análisis exploratorio (EDA)
- [ ] Feature engineering
- [ ] Entrenamiento y evaluación de modelos
- [ ] Selección del modelo final
