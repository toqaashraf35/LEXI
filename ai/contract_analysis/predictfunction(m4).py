import re

def normalize_arabic(text):
    text = re.sub(r'[إأآا]', 'ا', text)     # unify alef forms → ا
    text = re.sub(r'ى', 'ي', text)          # alef maksura → yeh  (fixes الثانى → الثاني)
    text = re.sub(r'ؤ', 'و', text)          # optional: hamza on waw
    text = re.sub(r'ئ', 'ي', text)          # optional: hamza on yeh
    text = re.sub(r'ة', 'ه', text)          # optional: teh marbuta → heh
    text = re.sub(r'[ًٌٍَُِّْـ]', '', text)  # strip diacritics/tatweel
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def predict_clause(clause, contract_type='عام', contract_subtype='عام'):
    full_text     = f'[{contract_type}] [{contract_subtype}] {normalize_arabic(clause)}'
    X_transformed = ridge_model.named_steps['tfidf'].transform([full_text])
    estimators    = ridge_model.named_steps['clf'].estimators_
    y_columns     = list(y.columns)

    raw_pred = []
    party_scores = {}  # ← نحتفظ بالـ scores

    for i, col in enumerate(y_columns):
        if col == 'risk_type_label':
            raw_pred.append(estimators[i].predict(X_transformed)[0])
        else:
            score = estimators[i].decision_function(X_transformed)[0]
            t     = best_thresholds_ridge.get(col, 0.0)
            raw_pred.append(1 if score >= t else 0)
            if col != 'risk':
                party_scores[col] = score  # ← خزّن الـ score

    risk       = int(raw_pred[0])
    party_cols = list(mlb.classes_)

    # ← بدل binary، خد الـ party الأعلى score لو فيه تعارض
    parties_raw = [party_cols[i] for i, v in enumerate(raw_pred[1:1+len(party_cols)]) if v == 1]

    if len(parties_raw) > 1:
        # لو أكثر من طرف، خد الـ party الأعلى score بس
        best_party = max(
            {p: party_scores[p] for p in parties_raw},
            key=lambda p: party_scores[p]
        )
        # إلا لو الفرق بين الـ scores صغير جداً → جميع الأطراف
        scores_list = [party_scores[p] for p in parties_raw]
        score_gap   = max(scores_list) - min(scores_list)

        if score_gap < 0.15:
            # الموديل مش متأكد → جميع الأطراف
            parties = ['جميع الأطراف']
        else:
            # فيه طرف واضح أعلى → خده بس
            parties = [best_party]
    else:
        parties = parties_raw

    risk_type_idx = int(raw_pred[-1])
    risk_type_en  = le_risk_type.classes_[risk_type_idx]
    risk_type_ar  = to_arabic_risk_type(risk_type_en)

    return {
        'clause':       clause,
        'risk':         risk,
        'parties':      parties if risk == 1 else [],
        'risk_type_en': risk_type_en if risk == 1 else 'none',
        'risk_type':    risk_type_ar if risk == 1 else 'لا يوجد',
    }