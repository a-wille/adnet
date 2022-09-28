

def load_context(request):
    # set username context for a session
    context = {}
    context['username'] = request.user.username
    return context