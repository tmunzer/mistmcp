REQ_TEMPLATE = """
    response = {request}
    await process_response(response)

"""

REQ_OPTIMIZED_TEMPLATE = """
    if {parameter}:
        response = {custom_request}
        await process_response(response)
    else:
        response = {request}
        await process_response(response)

"""
