import re


def fill_contract_template(
    template,
    inputs
):

    for key, value in inputs.items():

        pattern = r"\[" + re.escape(key) + r"\]"

        template = re.sub(
            pattern,
            str(value),
            template
        )

    return template