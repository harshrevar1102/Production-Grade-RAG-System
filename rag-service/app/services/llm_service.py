import ollama

from app.services.prompt_service import build_rag_prompt


MODEL_NAME = "llama3.2:latest"


def generate_answer(
    query: str,
    context: str
) -> str:

    prompt = build_rag_prompt(
        query=query,
        context=context
    )

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()