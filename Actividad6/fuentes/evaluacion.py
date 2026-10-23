"""Evaluación complementaria de modelos CIMA para la Actividad 6.

Usa los modelos congelados de Actividad 5 para la prueba reservada y hace CV
anidada sobre entrenamiento para estimar generalización y elegir umbrales.
No sobrescribe el dataset ni los modelos originales.
"""
from __future__ import annotations
import json
import warnings
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, ConfusionMatrixDisplay,
    roc_curve, roc_auc_score
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "datos" / "datos_limp"
MODEL_DIR = ROOT / "modelos"
OUT = ROOT / "resultados"
FIG = OUT / "graficas"
REPORTS = OUT / "reportes"
LABELS = ["INDIVIDUAL", "PAQUETE", "AMBIGUA", "FUERA_ALCANCE"]
POSITIVE = "INDIVIDUAL"
SEED = 20261015


def load_inputs():
    train_path = DATA_DIR / "entrenamiento.csv"
    test_path = DATA_DIR / "prueba.csv"
    for path in (train_path, test_path):
        if not path.is_file():
            raise FileNotFoundError(f"Falta archivo requerido: {path}")
    train = pd.read_csv(train_path, encoding="utf-8-sig", keep_default_na=False)
    test = pd.read_csv(test_path, encoding="utf-8-sig", keep_default_na=False)
    required = {"id", "texto_normalizado", "clase_real"}
    for name, df in (("entrenamiento", train), ("prueba", test)):
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"A entrenamiento/prueba les faltan columnas en {name}: {missing}")
        if df["texto_normalizado"].astype(str).str.strip().eq("").any():
            raise ValueError(f"Hay texto vacío en {name}")
        if not set(df["clase_real"]).issubset(LABELS):
            raise ValueError(f"Hay etiquetas desconocidas en {name}")
    overlap = set(train["texto_normalizado"]) & set(test["texto_normalizado"])
    if overlap:
        raise ValueError(f"Fuga de texto entre entrenamiento y prueba: {len(overlap)} textos")
    if len(train) != 102 or len(test) != 26:
        warnings.warn(f"Tamaños distintos a la versión A5 esperada: train={len(train)}, test={len(test)}")
    return train, test


def model_files():
    return {
        "Regresion_Logistica": MODEL_DIR / "Regresion_Logistica.joblib",
        "LinearSVC": MODEL_DIR / "LinearSVC.joblib",
    }


def get_model_scores(model, x, labels):
    """Devuelve las puntuaciones por clase y puntuación binaria operativa.

    Para LogisticRegression usa predict_proba. Para LinearSVC usa decision_function.
    La puntuación binaria SVC es margen de INDIVIDUAL menos la mejor alternativa;
    es un score, no una probabilidad calibrada.
    """
    classes = list(model.classes_)
    idx = classes.index(POSITIVE)
    if hasattr(model, "predict_proba"):
        class_scores = model.predict_proba(x)
        positive_score = class_scores[:, idx]
        score_kind = "probabilidad estimada"
    else:
        class_scores = model.decision_function(x)
        other_idx = [i for i, c in enumerate(classes) if c != POSITIVE]
        positive_score = class_scores[:, idx] - np.max(class_scores[:, other_idx], axis=1)
        score_kind = "margen de decisión (no es probabilidad)"
    # Reordenar las columnas en el orden canónico para ROC multiclase One-vs-Rest.
    order = [classes.index(label) for label in LABELS]
    class_scores_ordered = class_scores[:, order]
    return class_scores_ordered, positive_score, score_kind


def choose_threshold(oof_true, oof_pred, oof_score):
    """Umbral de mayor sensibilidad con cero falsas elegibilidades en OOF.

    Solo los casos que el clasificador multiclase ya predice como INDIVIDUAL
    pueden abrir el flujo individual; los demás se mandan a revisión.
    """
    oof_true = np.asarray(oof_true)
    oof_pred = np.asarray(oof_pred)
    oof_score = np.asarray(oof_score)
    candidates = np.unique(oof_score[oof_pred == POSITIVE])
    if candidates.size == 0:
        return float("inf"), {"oof_true_positives": 0, "oof_false_eligibilities": 0,
                              "oof_threshold_recall": 0.0, "rule": "abstención completa; no hubo predicciones INDIVIDUAL OOF"}
    valid = []
    n_positive = int(np.sum(oof_true == POSITIVE))
    for threshold in candidates:
        gate = (oof_pred == POSITIVE) & (oof_score >= threshold)
        tp = int(np.sum(gate & (oof_true == POSITIVE)))
        fp = int(np.sum(gate & (oof_true != POSITIVE)))
        if fp == 0:
            recall = tp / n_positive if n_positive else 0.0
            # Among thresholds with zero false eligibility, maximize TP; tie -> more conservative (higher threshold).
            valid.append((tp, float(threshold), recall))
    if not valid:
        return float("inf"), {"oof_true_positives": 0, "oof_false_eligibilities": 0,
                              "oof_threshold_recall": 0.0, "rule": "abstención completa; ningún umbral logra FP=0"}
    tp, threshold, recall = sorted(valid, key=lambda item: (item[0], item[1]), reverse=True)[0]
    gate = (oof_pred == POSITIVE) & (oof_score >= threshold)
    fp = int(np.sum(gate & (oof_true != POSITIVE)))
    return threshold, {"oof_true_positives": tp, "oof_false_eligibilities": fp,
                       "oof_threshold_recall": recall,
                       "rule": "maximizar TP sujeto a cero falsas elegibilidades OOF; empate: umbral mayor"}


def binary_operational(y_true, action):
    true_pos = np.asarray(y_true) == POSITIVE
    predicted_pos = np.asarray(action) == POSITIVE
    return {
        "binary_accuracy": float(accuracy_score(true_pos, predicted_pos)),
        "binary_precision_individual": float(precision_score(true_pos, predicted_pos, zero_division=0)),
        "binary_recall_individual": float(recall_score(true_pos, predicted_pos, zero_division=0)),
        "false_eligibility_count": int(np.sum((~true_pos) & predicted_pos)),
        "false_eligibility_rate": float(np.sum((~true_pos) & predicted_pos) / max(1, np.sum(~true_pos))),
        "non_individual_route_count": int(np.sum(~predicted_pos)),
        "true_individual_routed": int(np.sum(true_pos & predicted_pos)),
    }


def mcnemar_exact(y_true, pred_a, pred_b, name_a, name_b):
    correct_a = np.asarray(y_true) == np.asarray(pred_a)
    correct_b = np.asarray(y_true) == np.asarray(pred_b)
    a_only = int(np.sum(correct_a & ~correct_b))
    b_only = int(np.sum(~correct_a & correct_b))
    discordant = a_only + b_only
    p = float(binomtest(a_only, discordant, 0.5, alternative="two-sided").pvalue) if discordant else 1.0
    if p < 0.05:
        interp = "Diferencia estadística detectada con esta muestra; interpretar con cautela por n pequeño y datos sintéticos."
    else:
        interp = "No se detectó diferencia estadísticamente significativa; esto no demuestra equivalencia, especialmente con n pequeño."
    return {"comparacion": f"{name_a} vs {name_b}", "solo_A_correcto": a_only,
            "solo_B_correcto": b_only, "pares_discordantes": discordant,
            "p_valor_mcnemar_exacto": p, "interpretacion": interp}


def plot_confusion(y_true, y_pred, name, path):
    cm = confusion_matrix(y_true, y_pred, labels=LABELS)
    fig, ax = plt.subplots(figsize=(7, 5.5))
    disp = ConfusionMatrixDisplay(cm, display_labels=LABELS)
    disp.plot(ax=ax, cmap="Blues", colorbar=False, values_format="d")
    ax.set_title(f"Actividad 6 - {name}")
    ax.tick_params(axis="x", labelrotation=30)
    fig.tight_layout()
    fig.savefig(path, dpi=170, bbox_inches="tight")
    plt.close(fig)


def run_evaluation():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    train, test = load_inputs()
    x_train = train["texto_normalizado"].astype(str).tolist()
    y_train = train["clase_real"].astype(str).to_numpy()
    x_test = test["texto_normalizado"].astype(str).tolist()
    y_test = test["clase_real"].astype(str).to_numpy()
    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=SEED)

    metrics_rows, pred_rows, cv_rows, threshold_rows, class_rows = [], [], [], [], []
    scores_by_model, preds_by_model, binary_roc_data = {}, {}, {}
    reports = {}

    # Baseline majority class; it never sees the test labels while fitting.
    baseline = DummyClassifier(strategy="most_frequent")
    base_oof_pred = cross_val_predict(baseline, x_train, y_train, cv=cv, method="predict")
    baseline_cv_f1 = []
    for fold, (tr_i, va_i) in enumerate(cv.split(x_train, y_train), start=1):
        m = clone(baseline).fit(np.asarray(x_train)[tr_i], y_train[tr_i])
        pr = m.predict(np.asarray(x_train)[va_i])
        baseline_cv_f1.append(f1_score(y_train[va_i], pr, labels=LABELS, average="macro", zero_division=0))
        cv_rows.append({"modelo": "DummyClassifier_most_frequent", "fold": fold,
                        "f1_macro": baseline_cv_f1[-1], "accuracy": accuracy_score(y_train[va_i], pr)})
    baseline.fit(x_train, y_train)
    baseline_test = baseline.predict(x_test)
    base_auc_scores = None
    metrics_rows.append({"modelo": "DummyClassifier_most_frequent", "tipo": "baseline_prueba",
                         "accuracy": accuracy_score(y_test, baseline_test),
                         "precision_macro": precision_score(y_test, baseline_test, labels=LABELS, average="macro", zero_division=0),
                         "recall_macro": recall_score(y_test, baseline_test, labels=LABELS, average="macro", zero_division=0),
                         "f1_macro": f1_score(y_test, baseline_test, labels=LABELS, average="macro", zero_division=0),
                         "roc_auc_individual_vs_resto": np.nan, "threshold": np.nan,
                         **binary_operational(y_test, baseline_test)})
    reports["DummyClassifier_most_frequent"] = classification_report(y_test, baseline_test, labels=LABELS, output_dict=True, zero_division=0)
    plot_confusion(y_test, baseline_test, "DummyClassifier_most_frequent", FIG / "matriz_DummyClassifier.png")
    for rid, text, true, pred in zip(test["id"], x_test, y_test, baseline_test):
        pred_rows.append({"modelo": "DummyClassifier_most_frequent", "id": rid, "texto": text,
                          "clase_real": true, "prediccion": pred, "accion_umbral": "BASELINE"})

    # Evaluar modelos A5 congelados. La CV usa los hiperparámetros seleccionados en A5;
    # la prueba reservada permanece fuera de la selección del umbral.
    for model_name, model_path in model_files().items():
        if not model_path.is_file():
            raise FileNotFoundError(f"Falta modelo A5: {model_path}")
        final_model = joblib.load(model_path)
        pred = final_model.predict(x_test)
        class_scores, test_score, score_kind = get_model_scores(final_model, x_test, LABELS)
        classes = list(final_model.classes_)
        order = [classes.index(label) for label in LABELS]
        # ROC by class one-vs-rest; decision scores for LinearSVC are not probabilities.
        y_bin = np.column_stack([(y_test == label).astype(int) for label in LABELS])
        per_class_auc = {}
        fig, ax = plt.subplots(figsize=(7, 5.5))
        for idx, label in enumerate(LABELS):
            if len(np.unique(y_bin[:, idx])) == 2:
                fpr, tpr, _ = roc_curve(y_bin[:, idx], class_scores[:, idx])
                auc_value = roc_auc_score(y_bin[:, idx], class_scores[:, idx])
                per_class_auc[label] = float(auc_value)
                ax.plot(fpr, tpr, label=f"{label} (AUC={auc_value:.3f})")
            else:
                per_class_auc[label] = np.nan
        ax.plot([0, 1], [0, 1], "k--", label="Azar")
        ax.set(xlabel="Tasa de falsos positivos", ylabel="Tasa de verdaderos positivos",
               title=f"ROC One-vs-Rest - {model_name}")
        ax.legend(fontsize=8, loc="lower right")
        fig.tight_layout()
        fig.savefig(FIG / f"roc_ovr_{model_name}.png", dpi=170, bbox_inches="tight")
        plt.close(fig)
        binary_y = (y_test == POSITIVE).astype(int)
        binary_auc = float(roc_auc_score(binary_y, test_score))
        binary_roc_data[model_name] = (binary_y.copy(), test_score.copy(), binary_auc)
        macro_auc = float(np.nanmean(list(per_class_auc.values())))

        # Cross-validation OOF with the hyperparameters frozen from Activity 5.
        # This is intentionally not a new GridSearch; the saved models remain untouched.
        oof_pred = cross_val_predict(final_model, x_train, y_train, cv=cv, method="predict")
        score_method = "predict_proba" if hasattr(final_model, "predict_proba") else "decision_function"
        oof_class_scores = cross_val_predict(final_model, x_train, y_train, cv=cv, method=score_method)
        fitted_classes = list(final_model.classes_)
        positive_idx = fitted_classes.index(POSITIVE)
        if score_method == "predict_proba":
            oof_score = oof_class_scores[:, positive_idx]
        else:
            other_idx = [i for i, c in enumerate(fitted_classes) if c != POSITIVE]
            oof_score = oof_class_scores[:, positive_idx] - np.max(oof_class_scores[:, other_idx], axis=1)
        oof_fold_metrics = []
        for fold, (_, va_i) in enumerate(cv.split(x_train, y_train), start=1):
            fold_f1 = f1_score(y_train[va_i], oof_pred[va_i], labels=LABELS, average="macro", zero_division=0)
            fold_acc = accuracy_score(y_train[va_i], oof_pred[va_i])
            cv_rows.append({"modelo": model_name, "fold": fold,
                            "f1_macro": float(fold_f1), "accuracy": float(fold_acc),
                            "hiperparametros": "Congelados desde Actividad 5; sin nueva búsqueda"})
            oof_fold_metrics.append(float(fold_f1))
        threshold, threshold_meta = choose_threshold(y_train, oof_pred, oof_score)

        # Gate: only allow individual flow if class model predicts INDIVIDUAL and its score clears OOF threshold.
        gate = np.where((pred == POSITIVE) & (test_score >= threshold), POSITIVE, "REVISION_MANUAL")
        base_metrics = {
            "modelo": model_name, "tipo": "clasificacion_multiclase_prueba",
            "accuracy": float(accuracy_score(y_test, pred)),
            "precision_macro": float(precision_score(y_test, pred, labels=LABELS, average="macro", zero_division=0)),
            "recall_macro": float(recall_score(y_test, pred, labels=LABELS, average="macro", zero_division=0)),
            "f1_macro": float(f1_score(y_test, pred, labels=LABELS, average="macro", zero_division=0)),
            "roc_auc_individual_vs_resto": binary_auc, "roc_auc_ovr_macro_promedio_por_clase": macro_auc,
            "score_operativo": score_kind, "threshold": threshold,
            **binary_operational(y_test, pred),
        }
        metrics_rows.append(base_metrics)
        # Operational gated metrics use positive = individual route, all else = manual review.
        gate_stats = binary_operational(y_test, gate)
        metrics_rows.append({"modelo": model_name, "tipo": "politica_umbral_prueba",
                             "accuracy": np.nan, "precision_macro": np.nan, "recall_macro": np.nan,
                             "f1_macro": np.nan, "roc_auc_individual_vs_resto": binary_auc,
                             "roc_auc_ovr_macro_promedio_por_clase": np.nan, "score_operativo": score_kind,
                             "threshold": threshold,
                             "manual_review_count": int(np.sum(gate != POSITIVE)), **gate_stats})
        reports[model_name] = classification_report(y_test, pred, labels=LABELS, output_dict=True, zero_division=0)
        plot_confusion(y_test, pred, model_name, FIG / f"matriz_{model_name}.png")
        scores_by_model[model_name] = test_score
        preds_by_model[model_name] = pred
        for idx, label in enumerate(LABELS):
            class_rows.append({"modelo": model_name, "clase": label, **reports[model_name][label],
                               "roc_auc_ovr_clase": per_class_auc[label]})
        threshold_rows.append({"modelo": model_name, "threshold_oof": threshold,
                               "tipo_score": score_kind, **threshold_meta,
                               "casos_prueba_enrutados_individual": int(np.sum(gate == POSITIVE)),
                               "revision_manual_prueba": int(np.sum(gate != POSITIVE)),
                               **{f"prueba_{k}": v for k,v in gate_stats.items()}})
        for i, (rid, text, true, base_pred, action, score) in enumerate(zip(test["id"], x_test, y_test, pred, gate, test_score)):
            pred_rows.append({"modelo": model_name, "id": rid, "texto": text, "clase_real": true,
                              "prediccion": base_pred, "score_individual": float(score),
                              "tipo_score": score_kind, "umbral_oof": threshold,
                              "accion_umbral": action, "fold_oof_entrenamiento": ""})
        # Paired CV summary contains exactly one row per outer fold per model; OOF predictions generated above.

    metrics_df = pd.DataFrame(metrics_rows)
    metrics_df.to_csv(OUT / "metricas_actividad6.csv", index=False, encoding="utf-8-sig")
    cv_df = pd.DataFrame(cv_rows)
    cv_df.to_csv(OUT / "validacion_cruzada.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(threshold_rows).to_csv(OUT / "analisis_umbrales.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(pred_rows).to_csv(OUT / "predicciones_actividad6.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(class_rows).to_csv(OUT / "metricas_por_clase.csv", index=False, encoding="utf-8-sig")
    (REPORTS / "reportes_por_modelo.json").write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")

    # ROC operacional comparable: INDIVIDUAL frente a NO_INDIVIDUAL.
    fig, ax = plt.subplots(figsize=(7, 5.5))
    for model_name, (binary_y, score, auc_value) in binary_roc_data.items():
        fpr, tpr, _ = roc_curve(binary_y, score)
        ax.plot(fpr, tpr, label=f"{model_name} (AUC={auc_value:.3f})")
    ax.plot([0, 1], [0, 1], "k--", label="Azar")
    ax.set(xlabel="Tasa de falsos positivos", ylabel="Tasa de verdaderos positivos",
           title="ROC operativa: INDIVIDUAL vs. NO_INDIVIDUAL")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "roc_operativa_comparativa.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    # CV comparison plot: baseline vs nested model outer fold F1.
    cv_nonbaseline = cv_df[cv_df["modelo"].isin(["DummyClassifier_most_frequent", "Regresion_Logistica", "LinearSVC"])]
    fig, ax = plt.subplots(figsize=(8, 5.5))
    data = [cv_nonbaseline.loc[cv_nonbaseline.modelo == name, "f1_macro"].dropna().to_numpy()
            for name in ["DummyClassifier_most_frequent", "Regresion_Logistica", "LinearSVC"]]
    ax.boxplot(data, labels=["Baseline", "Regresión logística", "LinearSVC"], showmeans=True)
    ax.set_ylabel("F1 macro por pliegue")
    ax.set_title("Comparación de validación cruzada (4 pliegues)")
    fig.tight_layout()
    fig.savefig(FIG / "comparacion_cv_f1_macro.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    # A/B offline de políticas operativas: A = revisión manual para todos;
    # B = permitir flujo INDIVIDUAL solo si LogisticRegression supera el umbral OOF.
    lr_pred = preds_by_model["Regresion_Logistica"]
    lr_score = scores_by_model["Regresion_Logistica"]
    lr_threshold = float(pd.DataFrame(threshold_rows).query("modelo == 'Regresion_Logistica'")["threshold_oof"].iloc[0])
    lr_gate = np.where((lr_pred == POSITIVE) & (lr_score >= lr_threshold), POSITIVE, "REVISION_MANUAL")
    policy_a = np.repeat("REVISION_MANUAL", len(y_test))
    policy_b = lr_gate
    ab_rows = []
    for policy_name, policy in [("A_revision_manual_todos", policy_a), ("B_regresion_logistica_con_umbral", policy_b)]:
        stats = binary_operational(y_test, policy)
        ab_rows.append({"politica": policy_name, "n_casos": len(y_test), **stats,
                        "manual_review_count": int(np.sum(policy != POSITIVE)),
                        "accuracy_multiclase": np.nan,
                        "nota": "Simulación offline pareada sobre la misma prueba sintética; no es A/B real con usuarios ni asignación aleatoria."})
    pd.DataFrame(ab_rows).to_csv(OUT / "simulacion_ab_politicas.csv", index=False, encoding="utf-8-sig")

    # McNemar A/B offline on operational INDIVIDUAL-vs-rest decisions.
    lr_binary_prediction = np.where(preds_by_model["Regresion_Logistica"] == POSITIVE, POSITIVE, "NO_INDIVIDUAL")
    svc_binary_prediction = np.where(preds_by_model["LinearSVC"] == POSITIVE, POSITIVE, "NO_INDIVIDUAL")
    baseline_binary_prediction = np.where(baseline_test == POSITIVE, POSITIVE, "NO_INDIVIDUAL")
    gate_binary_prediction = np.where(lr_gate == POSITIVE, POSITIVE, "NO_INDIVIDUAL")
    binary_truth_labels = np.where(y_test == POSITIVE, POSITIVE, "NO_INDIVIDUAL")
    stat_rows = [
        mcnemar_exact(y_test, preds_by_model["Regresion_Logistica"], preds_by_model["LinearSVC"],
                      "Regresion_Logistica_multiclase", "LinearSVC_multiclase"),
        mcnemar_exact(y_test, preds_by_model["Regresion_Logistica"], baseline_test,
                      "Regresion_Logistica_multiclase", "DummyClassifier_multiclase"),
        mcnemar_exact(binary_truth_labels,
                      np.repeat("NO_INDIVIDUAL", len(y_test)), gate_binary_prediction,
                      "Politica_A_revision_manual_todos", "Politica_B_LR_umbral_revision"),
        mcnemar_exact(binary_truth_labels, lr_binary_prediction, baseline_binary_prediction,
                      "Politica_LR", "Politica_baseline_binaria"),
    ]
    stat_df = pd.DataFrame(stat_rows)
    stat_df.to_csv(OUT / "comparacion_estadistica.csv", index=False, encoding="utf-8-sig")

    metadata = {
        "actividad": "Actividad 6 - evaluación y validación CIMA",
        "dataset_version": "a5-v1.0",
        "train_n": int(len(train)), "test_n": int(len(test)), "seed": SEED,
        "threshold_method": "StratifiedKFold 4-fold OOF predictions from fixed Activity 5 model configurations; maximize true positives with zero false eligibility in OOF.",
        "test_used_for_threshold_selection": False,
        "cv_hyperparameters": "Frozen from Activity 5; CV evaluates these fixed configurations and does not perform a new search.",
        "ab_test_type": "offline paired policy simulation, not live randomized A/B test",
        "warning": "Test is synthetic and small; only two AMBIGUA test samples in A5 split; no production inference.",
    }
    (OUT / "metadatos_actividad6.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Actividad 6: evaluación completada.")
    print("Train/test:", len(train), len(test))
    print("\nMétricas principales:")
    cols = ["modelo", "tipo", "accuracy", "precision_macro", "recall_macro", "f1_macro",
            "roc_auc_individual_vs_resto", "threshold", "false_eligibility_count", "manual_review_count", "non_individual_route_count"]
    print(metrics_df[[c for c in cols if c in metrics_df.columns]].to_string(index=False))
    print("\nPruebas estadísticas (descriptivas, n pequeño):")
    print(stat_df.to_string(index=False))
    print("\nArchivos generados en:", OUT)
    return metrics_df

if __name__ == "__main__":
    run_evaluation()
