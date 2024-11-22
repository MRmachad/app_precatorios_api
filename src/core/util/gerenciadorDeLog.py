import traceback


def log_error(exception):
    error_type = type(exception).__name__  
    error_message = str(exception)  
    error_traceback = traceback.format_exc()  

    print(f"Tipo: {error_type}")
    print(f"Mensagem: {error_message}")
    print(f"Traceback:\n{error_traceback}")