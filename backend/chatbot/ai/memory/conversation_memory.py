MAX_HISTORY = 6


def build_conversation_context(history):

    if not history:

        return ""


    context = ""


    for msg in history[-MAX_HISTORY:]:

        role = msg.get(

            'role',
            'user'
        )

        content = msg.get(

            'content',
            ''
        )


        context += f"""

        {role}:
        {content}
        """


    return context.strip()