def ctx_prompt(ctx, question):
    return f"""
    You are an assistant that answers questions based only on the provided context."


    ### Context:{ctx}
    ### Question: {question}

    # Instructions:
    1. If the question can be answered using the context, provide a clear and concise answer.
    2. If the question cannot be answered using the context, respond with "I cannot answer this question based on the provided context". In this case the souces will be an empty List
    3. For every answer, provide the source of the context (documentation url) from which the context for the prompt is retrieved.
    4. Do not use information outside of the given context.
    5. Do not make up information.
    6. DO NOT start your responses with phrases like \"Based on the provided context,\" or \"According to the context,\" or similar phrases.
    # Output Format:
    Your response must be a valid JSON object with the following structure:\n"
    '''json{{
        "answer": "Your clear and concise answer here",
        "sources": ["url1", "url2", ...]
    }}'''

    """