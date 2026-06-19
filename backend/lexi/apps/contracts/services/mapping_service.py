def build_key_to_label_map(contract):
    mapping = {}

    for cf in contract.contract_fields.select_related("field"):
        mapping[cf.field.key] = cf.field.label

    return mapping


def convert_keys_to_labels(fields_data, key_label_map):
    converted = {}

    for key, value in fields_data.items():
        label = key_label_map.get(key)

        if label:
            converted[label] = value

    return converted