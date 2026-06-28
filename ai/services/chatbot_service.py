from chatbot.pipeline import rag_pipeline


def generate_answer(question, history):

    history_list = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in history
    ]

    answer = rag_pipeline(
        question=question,
        history=history_list,
    )

    return answer