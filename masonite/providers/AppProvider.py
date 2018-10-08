"""An AppProvider Service Provider."""

from config import application, middleware, storage

from masonite.autoload import Autoload
from masonite.commands import (AuthCommand, CommandCommand, ControllerCommand,
                               DownCommand, InfoCommand, InstallCommand,
                               JobCommand, KeyCommand, MiddlewareCommand,
                               MakeMigrationCommand, MigrateCommand, MigrateRefreshCommand,
                               MigrateStatusCommand, MigrateResetCommand, MigrateRollbackCommand,
                               ModelCommand, ProviderCommand, RoutesCommand,
                               SeedCommand, SeedRunCommand, ServeCommand,
                               TinkerCommand, UpCommand, ViewCommand, ValidatorCommand)

from masonite.exception_handler import ExceptionHandler
from masonite.helpers.routes import flatten_routes
from masonite.hook import Hook
from masonite.provider import ServiceProvider
from masonite.request import Request
from masonite.routes import Route
from routes import web


class AppProvider(ServiceProvider):

    def register(self):
        self.app.bind('HookHandler', Hook(self.app))
        self.app.bind('WebRoutes', flatten_routes(web.ROUTES))
        self.app.bind('Response', None)
        self.app.bind('Storage', storage)
        self.app.bind('Route', Route())
        self.app.bind('Request', Request())
        self.app.bind('Container', self.app)
        self.app.bind('ExceptionHandler', ExceptionHandler(self.app))
        self.app.bind('RouteMiddleware', middleware.ROUTE_MIDDLEWARE)
        self.app.bind('HttpMiddleware', middleware.HTTP_MIDDLEWARE)

        # Insert Commands
        self.app.bind('MasoniteAuthCommand', AuthCommand())
        self.app.bind('MasoniteCommandCommand', CommandCommand())
        self.app.bind('MasoniteControllerCommand', ControllerCommand())
        self.app.bind('MasoniteDownCommand', DownCommand())
        self.app.bind('MasoniteInfoCommand', InfoCommand())
        self.app.bind('MasoniteInstallCommand', InstallCommand())
        self.app.bind('MasoniteJobCommand', JobCommand())
        self.app.bind('MasoniteKeyCommand', KeyCommand())
        self.app.bind('MasoniteMakeMigrationCommand', MakeMigrationCommand())
        self.app.bind('MasoniteMiddlewareCommand', MiddlewareCommand())
        self.app.bind('MasoniteMigrateCommand', MigrateCommand())
        self.app.bind('MasoniteMigrateRefreshCommand', MigrateRefreshCommand())
        self.app.bind('MasoniteMigrateResetCommand', MigrateResetCommand())
        self.app.bind('MasoniteMigrateStatusCommand', MigrateStatusCommand())
        self.app.bind('MasoniteMigrateRollbackCommand',
                      MigrateRollbackCommand())
        self.app.bind('MasoniteModelCommand', ModelCommand())
        self.app.bind('MasoniteProviderCommand', ProviderCommand())
        self.app.bind('MasoniteViewCommand', ViewCommand())
        self.app.bind('MasoniteRoutesCommand', RoutesCommand())
        self.app.bind('MasoniteServeCommand', ServeCommand())
        self.app.bind('MasoniteSeedCommand', SeedCommand())
        self.app.bind('MasoniteSeedRunCommand', SeedRunCommand())
        self.app.bind('MasoniteTinkerCommand', TinkerCommand())
        self.app.bind('MasoniteUpCommand', UpCommand())
        self.app.bind('MasoniteValidatorCommand', ValidatorCommand())

        self._autoload(application.AUTOLOAD)
        self._set_application_debug_level()

    def boot(self, request: Request, route: Route):
        self.app.bind('Headers', [])
        self.app.bind('StatusCode', '404 Not Found')
        route.load_environ(self.app.make('Environ'))
        request.load_environ(self.app.make('Environ')).load_app(self.app)

    def _autoload(self, directories):
        Autoload(self.app).load(directories)

    def _set_application_debug_level(self):
        if self.app.make('Application').DEBUG == 'True':
            self.app.make('Application').DEBUG == True
        elif self.app.make('Application').DEBUG == 'False':
            self.app.make('Application').DEBUG == False
