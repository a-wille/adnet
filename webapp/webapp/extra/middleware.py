from .session import load_context

# necessary django configurations to have the frontend work correctly
class myMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        response = self.get_response(request)
        return response


    def process_view(self, request, a, b, c):
        if not request.user.is_authenticated:
            return
        if not request.session.get('context', False):
            load_context(request)
        return None