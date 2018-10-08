"""Module for the Pusher websocket driver."""

from masonite.contracts import BroadcastContract
from masonite.drivers import BaseDriver
from masonite.exceptions import DriverLibraryNotFound
from masonite.app import App


class BroadcastPusherDriver(BroadcastContract, BaseDriver):
    """Class for the Pusher websocket driver."""

    def __init__(self, app: App):
        """Pusher driver constructor.

        Arguments:
            BroadcastConfig {config.broadcast} -- Broadcast configuration.
        """
        self.config = app.make('BroadcastConfig')
        self.ssl_message = True

    def ssl(self, boolean):
        """Set whether to send data with SSL enabled.

        Arguments:
            boolean {bool} -- Boolean on whether to set SSL.

        Returns:
            self
        """
        self.ssl_message = boolean
        return self

    def channel(self, channels, message, event='base-event'):
        """Specify which channel(s) you want to send information to.

        Arguments:
            channels {string|list} -- Can be a string for the channel or a list of strings for the channels.
            message {string} -- The message you want to send to the channel(s)

        Keyword Arguments:
            event {string} -- The event you want broadcasted along with your data. (default: {'base-event'})

        Raises:
            DriverLibraryNotFound -- Thrown when pusher is not installed.

        Returns:
            string -- Returns the message sent.
        """
        try:
            import pusher
        except ImportError:
            raise DriverLibraryNotFound(
                'Could not find the "pusher" library. Please pip install this library running "pip install pusher"')

        pusher_client = pusher.Pusher(
            app_id=self.config.DRIVERS['pusher']['app_id'],
            key=self.config.DRIVERS['pusher']['client'],
            secret=self.config.DRIVERS['pusher']['secret'],
            ssl=self.ssl_message
        )

        if isinstance(message, str):
            message = {'message': message}

        if isinstance(channels, list):
            for channel in channels:
                pusher_client.trigger(channel, event, message)
        else:
            pusher_client.trigger(channels, event, message)

        return message
