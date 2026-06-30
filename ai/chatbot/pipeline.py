# from .llm import answer


# def rag_pipeline(question, history=None):

#     history = history or []

#     try:
#         return answer(
#             question,
#             history
#         )

#     except Exception as e:

#         return f"حدث خطأ: {str(e)}"


from .llm import answer_stream


def rag_pipeline(question, history=None):
    history = history or []

    try:
        return answer_stream(question, history)
    except Exception as e:
        def error_gen():
            yield f"حدث خطأ: {str(e)}"
        return error_gen()