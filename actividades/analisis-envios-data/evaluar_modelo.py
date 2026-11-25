"""
Prueba un modelo .joblib (Pipeline de scikit-learn) contra cada envios*.csv.

Uso:
    python evaluar_modelo.py <modelo.joblib> [carpeta_csv] [salida.txt]

Por cada archivo reporta: exactitud, exactitud de responder siempre la clase
mayoritaria, precisión / recall / f1 por medio y la matriz de confusión.
"""
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

CAMPOS = [
    "distancia_km", "peso_kg", "largo_cm", "ancho_cm", "alto_cm", "volumen_l",
    "fragil", "refrigerado", "valor_declarado_mxn", "hora_salida",
    "prioridad", "zona_destino", "clima", "trafico",
]
OBJETIVO = "medio_recomendado"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    modelo = joblib.load(sys.argv[1])
    carpeta = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / "datos"
    salida = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).parent / "resultados_modelo.txt"

    conocidos = list(modelo.classes_)
    lineas = [f"Modelo: {Path(sys.argv[1]).name}  | clases que conoce: {conocidos}", ""]
    resumen = []

    for csv in sorted(carpeta.glob("envios*.csv")):
        df = pd.read_csv(csv)
        real = df[OBJETIVO]
        pred = modelo.predict(df[CAMPOS])
        exactitud = accuracy_score(real, pred)
        mayoritaria = real.value_counts(normalize=True).iloc[0]
        resumen.append((csv.stem, exactitud, real.value_counts().index[0], mayoritaria))

        etiquetas = sorted(set(real) | set(pred))
        matriz = pd.DataFrame(confusion_matrix(real, pred, labels=etiquetas),
                              index=[f"real_{e}" for e in etiquetas],
                              columns=[f"pred_{e}" for e in etiquetas])
        lineas += [
            f"===== {csv.stem} =====",
            f"Exactitud: {exactitud:.3%}   | siempre '{real.value_counts().index[0]}': {mayoritaria:.3%}",
            classification_report(real, pred, labels=etiquetas, zero_division=0, digits=3),
            matriz.to_string(),
            "",
        ]

    lineas.append("===== RESUMEN =====")
    lineas.append(f"{'archivo':<9} {'exactitud':>10} {'mayoritaria':>22}")
    for nombre, exa, clase, may in resumen:
        lineas.append(f"{nombre:<9} {exa:>10.2%} {clase + ' ' + format(may, '.1%'):>22}")

    texto = "\n".join(lineas)
    salida.write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
