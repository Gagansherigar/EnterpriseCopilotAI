async def escalate_node(state):
    state["answer"] = (
        "I'm not confident enough to answer this — escalating to a human.\n"
        "Please contact support@quickbite.com"
    )
    return state