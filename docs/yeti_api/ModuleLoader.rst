
Module Loader
-------------

The Module Loader class is the third layer of yeti. It's primary feature is to
dynamically load modules straight from their python files.

It loads modules either via filename (with :meth:`load(module_path)`), or by setting a
fallback list (:meth:`add_fallback()` and :meth:`set_fallback()`). A fallback list
specifies a list of python filenames, each containing a class which will be loaded as a
module. Calling :meth:`load()` with no arguments will cause it to load the first module
on the fallback list. If at any time that module throws an uncaught exception, it will be
unloaded and replaced with the next module on the fallback list.

Most of the functionality of Module Loaders are contained in asyncio coroutines, and are
run in the currently loaded context. Therefore you must :meth:`set_context()` before loading
a module.

.. autoclass:: yeti.ModuleLoader
    :members:
    :undoc-members:
    :show-inheritance: