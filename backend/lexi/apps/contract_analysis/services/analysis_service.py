import pickle
import numpy as np
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / 'ai' / 'contract_analysis' / 'arabic_legal_model'

# Lazy loading - load only when first needed
_ridge_model = None
_best_thresholds_ridge = None
_mlb = None
_le_risk_type = None
_RISK_TYPE_AR = None
_y = None


def _load(filename):
    with open(MODELS_DIR / filename, 'rb') as f:
        return pickle.load(f)


def _load_models():
    global _ridge_model, _best_thresholds_ridge, _mlb, _le_risk_type, _RISK_TYPE_AR, _y
    if _ridge_model is None:
        _ridge_model           = _load('ridge_model_best.pkl')
        _best_thresholds_ridge = _load('ridge_thresholds.pkl')
        _mlb                   = _load('mlb.pkl')
        _le_risk_type          = _load('le_risk_type.pkl')
        _RISK_TYPE_AR          = _load('risk_type_ar_map.pkl')
        _y                     = _load('y.pkl')


def predict_clause(clause, contract_type='عام', contract_subtype='عام'):
    _load_models()  # loads only on first call

    full_text     = f'[{contract_type}] [{contract_subtype}] {clause}'
    X_transformed = _ridge_model.named_steps['tfidf'].transform([full_text])
    estimators    = _ridge_model.named_steps['clf'].estimators_
    y_columns     = list(_y.columns)

    raw_pred = []
    for i, col in enumerate(y_columns):
        if col == 'risk_type_label':
            raw_pred.append(estimators[i].predict(X_transformed)[0])
        else:
            score = estimators[i].decision_function(X_transformed)[0]
            t     = _best_thresholds_ridge[col]
            raw_pred.append(1 if score >= t else 0)

    risk       = int(raw_pred[0])
    party_cols = list(_mlb.classes_)
    parties    = [party_cols[i] for i, v in enumerate(raw_pred[1:1+len(party_cols)]) if v == 1]

    risk_type_idx = int(raw_pred[-1])
    risk_type_en  = _le_risk_type.classes_[risk_type_idx]
    risk_type_ar  = _RISK_TYPE_AR.get(risk_type_en, risk_type_en)

    return {
        'risk':         risk,
        'risk_parties': parties      if risk == 1 else [],
        'risk_type':    risk_type_ar if risk == 1 else None,
    }