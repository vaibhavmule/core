import pytest

from masonite.app import App
from masonite.exception_handler import ExceptionHandler
from masonite.exceptions import MissingContainerBindingNotFound
from masonite.hook import Hook
from masonite.view import View


class ApplicationMock:
    DEBUG = True


class StorageMock:
    STATICFILES = {}


class TestException:

    def setup_method(self):
        self.app = App()
        self.app.bind('Application', ApplicationMock)
        self.app.bind('View', View(self.app).render)
        self.app.bind('Storage', StorageMock)
        self.app.bind('ExceptionHandler', ExceptionHandler(self.app))
        self.app.bind('HookHandler', Hook(self.app))

    def test_exception_returns_none_when_debug_is_false(self):
        self.app.make('Application').DEBUG = False
        assert self.app.make('ExceptionHandler').load_exception(KeyError) is None
