"""Core of the IOC Container."""

import inspect

from masonite.exceptions import (ContainerError,
                                 MissingContainerBindingNotFound,
                                 StrictContainerException)


class App:
    """Core of the Service Container.

    Performs bindings and resolving of objects to and from the container.
    """

    def __init__(self, strict=False, override=True, resolve_parameters=False):
        """App class constructor."""
        self.providers = {}
        self.strict = strict
        self.override = override
        self.resolve_parameters = resolve_parameters
        self._hooks = {
            'make': {},
            'bind': {},
            'resolve': {},
        }

        self.swaps = {}

    def bind(self, name, class_obj):
        """Bind classes into the container with a key value pair.

        Arguments:
            name {string} -- Name of the key you want to bind the object to
            class_obj {object} -- The object you want to bind

        Returns:
            self
        """
        if self.strict and name in self.providers:
            raise StrictContainerException(
                'You cannot override a key inside a strict container')

        if self.override or name not in self.providers:
            self.fire_hook('bind', name, class_obj)
            self.providers.update({name: class_obj})

        return self

    def simple(self, obj):
        """Easy way to bind classes into the container by using passing the object only.

        Automatically generates the key for the binding process.

        Arguments:
            class_obj {object} -- The object you want to bind

        Returns:
            self
        """
        self.bind(obj if inspect.isclass(obj) else obj.__class__, obj)
        return self

    def make(self, name):
        """Retrieve a class from the container by key.

        Arguments:
            name {string} -- Key in the container that you want to get.

        Raises:
            MissingContainerBindingNotFound -- Raised if the key is not in the container.

        Returns:
            object -- Returns the object that is fetched.
        """
        if name in self.providers:
            obj = self.providers[name]
            self.fire_hook('make', name, obj)
            return obj
        elif inspect.isclass(name):
            obj = self._find_obj(name)
            self.fire_hook('make', name, obj)
            return obj

        raise MissingContainerBindingNotFound(
            "{0} key was not found in the container".format(name))

    def has(self, name):
        """Check if a key exists in the container.

        Arguments:
            name {string} -- Key you want to check for in the container

        Returns:
            bool
        """
        if isinstance(name, str):
            return name in self.providers
        else:
            try:
                self._find_obj(name)
                return True
            except MissingContainerBindingNotFound:
                return False

        return False

    def helper(self):
        """Add a helper to create builtin functions.

        Used to more simply return
        instances of this class when building helpers.

        Returns:
            self
        """
        return self

    def resolve(self, obj):
        """Take an object such as a function or class method and resolves it's parameters from objects in the container.

        Arguments:
            obj {object} -- The object you want to resolve objects from via this container.

        Returns:
            object -- The object you tried resolving but with the correct dependencies injected.
        """
        provider_list = []

        for _, value in inspect.signature(obj).parameters.items():
            if ':' in str(value):
                provider_list.append(self._find_annotated_parameter(value))
            elif self.resolve_parameters:
                provider_list.append(self._find_parameter(value))
            else:
                raise ContainerError(
                    "This container is not set to resolve parameters. You can set this in the container"
                    " constructor using the 'resolve_parameters=True' keyword argument.")

        return obj(*provider_list)

    def collect(self, search):
        """Fetch a dictionary of objects using a search query.

        Arguments:
            search {string|object} -- The string or object you want to search for.

        Raises:
            AttributeError -- Thrown if there is no wildcard in the search string

        Returns:
            dict -- Returns a dictionary of collected objects and their key bindings.
        """
        provider_list = {}
        if isinstance(search, str):
            # Search Can Be:
            #    '*ExceptionHook'
            #    'Sentry*'
            #    'Sentry*Hook'
            for key, value in self.providers.items():
                if search.startswith('*'):
                    if key.endswith(search.split('*')[1]):
                        provider_list.update({key: value})
                elif search.endswith('*'):
                    if key.startswith(search.split('*')[0]):
                        provider_list.update({key: value})
                elif '*' in search:
                    split_search = search.split('*')
                    if key.startswith(split_search[0]) and key.endswith(split_search[1]):
                        provider_list.update({key: value})
                else:
                    raise AttributeError(
                        "There is no '*' in your collection search")
        else:
            for provider_key, provider_class in self.providers.items():
                if inspect.isclass(provider_class) and issubclass(provider_class, search):
                    provider_list.update({provider_key: provider_class})

        return provider_list

    def _find_annotated_parameter(self, parameter):
        """Find a given annotation in the container.

        Arguments:
            parameter {object} -- The object to find in the container.

        Raises:
            ContainerError -- Thrown when the dependency is not found in the container.

        Returns:
            object -- Returns the object found in the container.
        """
        if parameter.annotation in self.swaps:
            obj = self.swaps[parameter.annotation]
            if callable(obj):
                return self.swaps[parameter.annotation](parameter.annotation, self)
            return obj

        for _, provider_class in self.providers.items():

            if parameter.annotation == provider_class or parameter.annotation == provider_class.__class__:
                obj = provider_class
                self.fire_hook('resolve', parameter, obj)

                return obj
            elif inspect.isclass(provider_class) and issubclass(provider_class, parameter.annotation) or issubclass(provider_class.__class__, parameter.annotation):
                obj = provider_class
                self.fire_hook('resolve', parameter, obj)
                return obj

        raise ContainerError(
            'The dependency with the {0} annotation could not be resolved by the container'.format(parameter))

    def _find_parameter(self, parameter):
        """Find a parameter in the container.

        Arguments:
            parameter {string} -- Parameter to search for.

        Raises:
            ContainerError -- Thrown when the dependency is not found in the container.

        Returns:
            object -- Returns the object found in the container
        """
        parameter = str(parameter)
        if parameter is not 'self' and parameter in self.providers:
            obj = self.providers[parameter]
            self.fire_hook('resolve', parameter, obj)
            return obj
        raise ContainerError(
            'The dependency with the key of {0} could not be found in the container'.format(
                parameter)
        )

    def on_bind(self, key, obj):
        """Set some listeners for when a specific key or class in binded to the container.

        Arguments:
            key {string|object} -- The key can be a string or an object to listen for
            obj {object} -- Should be a function or class method

        Returns:
            self
        """
        return self._bind_hook('bind', key, obj)

    def on_make(self, key, obj):
        """Set some listeners for when a specific key or class is made from the container.

        Arguments:
            key {string|object} -- The key can be a string or an object to listen for
            obj {object} -- Should be a function or class method

        Returns:
            self
        """
        return self._bind_hook('make', key, obj)

    def on_resolve(self, key, obj):
        """Set some listeners for when a specific key or class is resolved from the container.

        Arguments:
            key {string|object} -- The key can be a string or an object to listen for
            obj {object} -- Should be a function or class method

        Returns:
            self
        """
        return self._bind_hook('resolve', key, obj)

    def swap(self, obj, callback):
        self.swaps.update({obj: callback})
        return self

    def fire_hook(self, action, key, obj):
        """Fire a specific hook based on a key or object.

        Arguments:
            action {string} -- Should be the action to fire (bind|make|resolve)
            key {string|object} -- The key can be a string or an object to listen for
            obj {object} -- Should be a function or class method

        Returns:
            None
        """
        if str(key) in self._hooks[action] or \
                inspect.isclass(obj) and \
                obj in self._hooks[action] or obj.__class__ in self._hooks[action]:

            for hook, hook_list in self._hooks[action].items():
                for hook_obj in hook_list:
                    hook_obj(obj, self)

    def _bind_hook(self, hook, key, obj):
        """Internal method used to abstract away the logic for binding an listener to the container hooks.

        Arguments:
            hook {string} -- The hook you want to listen for (bind|make|resolve)
            key {string|object} -- The key to save for the listener
            obj {object} -- Should be a function or class method

        Returns:
            self
        """
        if key in self._hooks[hook]:
            self._hooks[hook][key].append(obj)
        else:
            self._hooks[hook].update({key: [obj]})
        return self

    def _find_obj(self, obj):
        """Find an object in the container.

        Arguments:
            obj {object} -- Any object in the container

        Raises:
            MissingContainerBindingNotFound -- Raised when the object cannot be found.

        Returns:
            object -- Returns the object in the container
        """
        for _, provider_class in self.providers.items():
            if obj == provider_class or obj == provider_class.__class__:
                return_obj = provider_class
                self.fire_hook('resolve', obj, return_obj)
                return return_obj
            elif inspect.isclass(provider_class) and issubclass(provider_class, obj) or issubclass(provider_class.__class__, obj):
                return_obj = provider_class
                self.fire_hook('resolve', obj, return_obj)
                return return_obj

        raise MissingContainerBindingNotFound(
            'The dependency with the {0} annotation could not be resolved by the container'.format(obj))
