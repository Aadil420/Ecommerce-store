# yourapp/context_processors.py
def add_username_to_context(request):
    if request.user.is_authenticated:
        return {'username': request.user.username}
    return {}