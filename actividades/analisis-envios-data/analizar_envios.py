"""
Análisis comparativo de varios CSV de envíos (envios1.csv ... envios6.csv).

Uso:
    python analisis/analizar_envios.py carpeta_con_csvs  [carpeta_salida]

Genera gráficas PNG + un resumen en texto (resumen.txt) en la carpeta de salida.
Requiere: pandas, numpy, matplotlib  (pip install pandas matplotlib)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

NUM = ["distancia_km", "peso_kg", "largo_cm", "ancho_cm", "alto_cm",
       "volumen_l", "valor_declarado_mxn", "hora_salida"]
CAT = ["prioridad", "zona_destino", "clima", "trafico", "fragil", "refrigerado"]
TARGET = "medio_recomendado"
MEDIOS = ["bicicleta", "dron", "moto", "camioneta"]
COLORES = {"bicicleta": "#2a9d8f", "dron": "#8ab17d", "moto": "#e9c46a", "camioneta": "#e76f51"}


def ks(a, b):
    """Estadístico Kolmogorov-Smirnov de 2 muestras (0 = idénticas, 1 = totalmente distintas)."""
    a, b = np.sort(a), np.sort(b)
    grid = np.concatenate([a, b])
    cdf_a = np.searchsorted(a, grid, side="right") / len(a)
    cdf_b = np.searchsorted(b, grid, side="right") / len(b)
    return float(np.max(np.abs(cdf_a - cdf_b)))


def cargar(carpeta):
    archivos = sorted(Path(carpeta).glob("*.csv"))
    if not archivos:
        sys.exit(f"No hay CSV en {carpeta}")
    partes = []
    for f in archivos:
        d = pd.read_csv(f)
        d["archivo"] = f.stem
        d["fila"] = np.arange(len(d))
        partes.append(d)
    return pd.concat(partes, ignore_index=True)


def guardar(fig, out, nombre):
    fig.tight_layout()
    fig.savefig(out / nombre, dpi=120)
    plt.close(fig)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    carpeta = sys.argv[1] if len(sys.argv) > 1 else "."
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "resultados_envios")
    out.mkdir(parents=True, exist_ok=True)

    df = cargar(carpeta)
    # Agrega cualquier clase inesperada (p. ej. "eskuter") en vez de ignorarla
    global MEDIOS
    extra = sorted(set(df[TARGET]) - set(MEDIOS))
    MEDIOS = [m for m in MEDIOS if m in set(df[TARGET])] + extra
    paleta = ["#6c5ce7", "#d63384", "#457b9d", "#8d6e63"]
    for i, m in enumerate(extra):
        COLORES.setdefault(m, paleta[i % len(paleta)])
    archivos = sorted(df["archivo"].unique())
    txt = []
    p = txt.append

    # ---------- 1. Calidad de datos ----------
    p("=== CALIDAD DE DATOS ===")
    for a in archivos:
        d = df[df.archivo == a]
        p(f"{a}: {len(d)} filas | nulos={int(d.isna().sum().sum())} | "
          f"ids {d.id_envio.min()} .. {d.id_envio.max()} | "
          f"filas duplicadas dentro={int(d.drop(columns=['archivo', 'fila']).duplicated().sum())}")
    ids_rep = df.id_envio.duplicated(keep=False)
    p(f"\nIDs que aparecen en más de una fila (todos los archivos): {int(ids_rep.sum())}")
    contenido = df.drop(columns=["archivo", "fila", "id_envio"])
    p(f"Registros idénticos (ignorando id) repetidos entre archivos: {int(contenido.duplicated().sum())}")

    # Solapamiento de IDs entre pares de archivos
    sets = {a: set(df.loc[df.archivo == a, "id_envio"]) for a in archivos}
    sol = pd.DataFrame([[len(sets[x] & sets[y]) for y in archivos] for x in archivos],
                       index=archivos, columns=archivos)
    p("\nIDs compartidos entre archivos:\n" + sol.to_string())

    # Volumen calculado vs declarado
    vol_calc = df.largo_cm * df.ancho_cm * df.alto_cm / 1000
    err = (vol_calc - df.volumen_l).abs()
    p(f"\nFilas donde volumen_l no cuadra con largo*ancho*alto (>0.5 L): {int((err > 0.5).sum())}")

    # Outliers de valor declarado (IQR)
    q1, q3 = df.valor_declarado_mxn.quantile([.25, .75])
    lim = q3 + 3 * (q3 - q1)
    p(f"Valores declarados atípicos (> {lim:,.0f} MXN): {int((df.valor_declarado_mxn > lim).sum())} "
      f"| máximo {df.valor_declarado_mxn.max():,.2f}")

    # ---------- 2. Qué tan mezclados están ----------
    p("\n=== ¿QUÉ TAN MEZCLADOS / PARECIDOS SON LOS ARCHIVOS? ===")
    prop = pd.crosstab(df.archivo, df[TARGET], normalize="index").reindex(columns=MEDIOS).fillna(0)
    p("Proporción de cada medio por archivo:\n" + (prop * 100).round(1).to_string())

    ks_tab = pd.DataFrame(index=archivos, columns=NUM, dtype=float)
    for a in archivos:
        dentro, fuera = df[df.archivo == a], df[df.archivo != a]
        for c in NUM:
            ks_tab.loc[a, c] = ks(dentro[c].values, fuera[c].values) if len(fuera) else 0.0
    p("\nKS de cada archivo contra el resto (≈0.00-0.03 = misma distribución; >0.10 = distinto):\n"
      + ks_tab.round(3).to_string())

    # Mezcla del orden: ¿las clases están agrupadas por filas o barajadas?
    p("\nOrden de filas (rachas de la misma clase; barajado ≈ 1.4, ordenado >> 10):")
    for a in archivos:
        y = df.loc[df.archivo == a, TARGET].values
        rachas = 1 + np.sum(y[1:] != y[:-1])
        p(f"  {a}: longitud media de racha = {len(y) / rachas:.2f}")

    # ---------- 3. Información relevante ----------
    p("\n=== PERFIL POR MEDIO RECOMENDADO (medianas) ===")
    p(df.groupby(TARGET)[NUM].median().reindex(MEDIOS).round(2).to_string())
    p("\nRangos (min - max) por medio:")
    for c in ["distancia_km", "peso_kg", "volumen_l"]:
        r = df.groupby(TARGET)[c].agg(["min", "max"]).reindex(MEDIOS)
        p(f"  {c}:\n" + r.to_string())
    p("\nRefrigerado -> medio:\n" + pd.crosstab(df.refrigerado, df[TARGET]).to_string())
    p("\nZona rural -> medio:\n" + pd.crosstab(df.zona_destino, df[TARGET]).to_string())
    p("\nClima -> medio:\n" + pd.crosstab(df.clima, df[TARGET]).to_string())

    (out / "resumen.txt").write_text("\n".join(txt), encoding="utf-8")
    print("\n".join(txt))

    # ---------- GRÁFICAS ----------
    # 01 proporción de clases por archivo
    fig, ax = plt.subplots(figsize=(9, 4.5))
    izq = np.zeros(len(prop))
    for m in MEDIOS:
        ax.barh(prop.index, prop[m], left=izq, color=COLORES[m], label=m)
        for i, (l, v) in enumerate(zip(izq, prop[m])):
            if v > .04:
                ax.text(l + v / 2, i, f"{v:.0%}", ha="center", va="center", fontsize=8)
        izq += prop[m].values
    ax.set_title("Proporción de medio recomendado por archivo")
    ax.legend(ncol=4, loc="lower center", bbox_to_anchor=(.5, -.25))
    guardar(fig, out, "01_clases_por_archivo.png")

    # 02 distribuciones numéricas por archivo (histogramas superpuestos)
    fig, axes = plt.subplots(2, 4, figsize=(16, 7))
    for ax, c in zip(axes.flat, NUM):
        datos = df[c].clip(upper=df[c].quantile(.99))
        bins = np.histogram_bin_edges(datos, 40)
        for a in archivos:
            ax.hist(datos[df.archivo == a], bins=bins, density=True, histtype="step", label=a)
        ax.set_title(c)
    axes.flat[0].legend(fontsize=7)
    fig.suptitle("Distribución de variables numéricas por archivo (si se enciman, están bien mezclados)")
    guardar(fig, out, "02_distribuciones_por_archivo.png")

    # 03 heatmap KS
    fig, ax = plt.subplots(figsize=(10, .6 * len(archivos) + 2))
    im = ax.imshow(ks_tab.values, cmap="Reds", vmin=0, vmax=max(.15, ks_tab.values.max()))
    ax.set_xticks(range(len(NUM)), NUM, rotation=35, ha="right")
    ax.set_yticks(range(len(archivos)), archivos)
    for i in range(len(archivos)):
        for j in range(len(NUM)):
            ax.text(j, i, f"{ks_tab.values[i, j]:.3f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="KS (0 = idéntico)")
    ax.set_title("Diferencia de cada archivo contra el resto (Kolmogorov-Smirnov)")
    guardar(fig, out, "03_heatmap_ks.png")

    # 04 categóricas por archivo
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))
    for ax, c in zip(axes.flat, CAT):
        t = pd.crosstab(df.archivo, df[c], normalize="index")
        t.plot(kind="bar", ax=ax, width=.8)
        ax.set_title(c); ax.set_xlabel(""); ax.legend(fontsize=7)
        ax.tick_params(axis="x", rotation=30)
    fig.suptitle("Variables categóricas: proporción por archivo")
    guardar(fig, out, "04_categoricas_por_archivo.png")

    # 05 orden de filas: proporción móvil de cada clase
    fig, axes = plt.subplots(len(archivos), 1, figsize=(12, 2.2 * len(archivos)), sharex=True, squeeze=False)
    for ax, a in zip(axes[:, 0], archivos):
        d = df[df.archivo == a]
        dummies = pd.get_dummies(d[TARGET]).reindex(columns=MEDIOS, fill_value=0).astype(float)
        movil = dummies.rolling(max(50, len(d) // 50), min_periods=1).mean()
        ax.stackplot(np.arange(len(d)), movil.T.values, colors=[COLORES[m] for m in MEDIOS], labels=MEDIOS)
        ax.set_ylabel(a, rotation=0, ha="right"); ax.set_ylim(0, 1)
    axes[0, 0].set_title("Proporción móvil de clases a lo largo de las filas (franjas planas = bien barajado)")
    axes[-1, 0].set_xlabel("número de fila")
    axes[0, 0].legend(ncol=4, loc="upper right", fontsize=7)
    guardar(fig, out, "05_orden_filas.png")

    # 06 distancia vs peso coloreado por medio
    fig, ax = plt.subplots(figsize=(9, 6))
    muestra = df.sample(min(len(df), 15000), random_state=0)
    for m in MEDIOS:
        s = muestra[muestra[TARGET] == m]
        ax.scatter(s.distancia_km, s.peso_kg, s=4, alpha=.4, color=COLORES[m], label=m)
    ax.set_xlabel("distancia_km"); ax.set_ylabel("peso_kg")
    ax.set_title("Distancia vs peso según medio recomendado")
    ax.legend(markerscale=4)
    guardar(fig, out, "06_distancia_vs_peso.png")

    # 07 boxplots por medio
    fig, axes = plt.subplots(2, 4, figsize=(16, 7))
    for ax, c in zip(axes.flat, NUM):
        datos = [df.loc[df[TARGET] == m, c] for m in MEDIOS]
        b = ax.boxplot(datos, tick_labels=MEDIOS, showfliers=False, patch_artist=True)
        for patch, m in zip(b["boxes"], MEDIOS):
            patch.set_facecolor(COLORES[m])
        ax.set_title(c); ax.tick_params(axis="x", rotation=30)
    fig.suptitle("Variables numéricas por medio recomendado (sin atípicos)")
    guardar(fig, out, "07_boxplots_por_medio.png")

    # 08 correlación
    corr_df = df[NUM + ["fragil", "refrigerado"]].copy()
    for m in MEDIOS:
        corr_df[f"es_{m}"] = (df[TARGET] == m).astype(int)
    corr = corr_df.corr()
    fig, ax = plt.subplots(figsize=(11, 9))
    im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(corr)), corr.columns)
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center", fontsize=7)
    fig.colorbar(im, ax=ax)
    ax.set_title("Matriz de correlación")
    guardar(fig, out, "08_correlacion.png")

    # 09 clima / refrigerado / zona vs medio
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    for ax, c in zip(axes, ["clima", "refrigerado", "zona_destino"]):
        t = pd.crosstab(df[c], df[TARGET], normalize="index").reindex(columns=MEDIOS).fillna(0)
        t.plot(kind="bar", stacked=True, ax=ax, color=[COLORES[m] for m in MEDIOS], legend=False)
        ax.set_title(f"{c} → medio"); ax.set_xlabel(""); ax.tick_params(axis="x", rotation=0)
    axes[-1].legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    guardar(fig, out, "09_condiciones_vs_medio.png")

    print(f"\nGráficas y resumen guardados en: {out.resolve()}")


if __name__ == "__main__":
    main()
