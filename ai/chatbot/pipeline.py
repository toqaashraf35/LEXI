from .llm import answer


def rag_pipeline(question, history=None):

    history = history or []

    try:
        return answer(
            question,
            history
        )

    except Exception as e:

        return f"حدث خطأ: {str(e)}"