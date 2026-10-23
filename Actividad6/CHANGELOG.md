# CHANGELOG — Actividad 6

## 0.1.0 — Estructura inicial de evaluación
- Se reutilizan datos versionados y modelos `.joblib` de Actividad 5 sin sobrescribirlos.
- Se añadieron matriz de confusión, métricas multiclase, ROC/AUC One-vs-Rest y ROC operativa `INDIVIDUAL` frente a resto.
- Se agregó `DummyClassifier` como baseline.
- Se agregó validación cruzada estratificada OOF de cuatro pliegues con hiperparámetros congelados desde A5.
- Se añadió selección de umbral usando puntuaciones OOF de entrenamiento, con regla de cero falsas elegibilidades y máxima cantidad de positivos aceptados.
- Se añadieron comparaciones pareadas de McNemar exacto y simulación offline de políticas A/B.
- Se documentaron los límites de inferencia de la prueba sintética pequeña y la diferencia entre score de LinearSVC y probabilidad calibrada.
