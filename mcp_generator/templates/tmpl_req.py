REQ_TEMPLATE = """
    try:
        response = {request}
        await process_response(response)
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
"""

REQ_OPTIMIZED_TEMPLATE = """
    try:
        if {parameter}:
            response = {custom_request}
            await process_response(response)
        else:
            response = {request}
            await process_response(response)
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
"""
