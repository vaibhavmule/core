""" CSRF Middleware """
from masonite.exceptions import InvalidCSRFToken
from masonite.request import Request
from masonite.auth import Csrf
from masonite.view import View
from jinja2 import Markup


class CsrfMiddleware:
    """ Verify CSRF Token Middleware """

    exempt = ['/']

    def __init__(self, request: Request, csrf: Csrf, view: View):
        self.request = request
        self.csrf = csrf
        self.view = view

    def before(self):
        token = self.__verify_csrf_token()

        self.view.share({
            'csrf_field': Markup("<input type='hidden' name='__token' value='{0}' />".format(token)),
            'csrf_token': token
        })

    def after(self):
        pass

    def __in_exempt(self):
        """
        Determine if the request has a URI that should pass
        through CSRF verification.
        """

        if self.request.path in self.exempt:
            return True
        else:
            return False

    def __verify_csrf_token(self):
        """
        Verify si csrf token in post is valid.
        """

        if self.request.is_post() and not self.__in_exempt():
            token = self.request.input('__token')
            if not self.csrf.verify_csrf_token(token):
                raise InvalidCSRFToken("Invalid CSRF token.")
        else:
            token = self.csrf.generate_csrf_token()

        return token
