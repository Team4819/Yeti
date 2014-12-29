def test_module_load(yeti, context):
    loader = yeti.ModuleLoader()
    loader.set_context(context)
    loader.load("resources.module_loader.module1")
    context.run_for(.25)
    assert loader.get_module().name == "ModuleUno"


def test_module_fallback(yeti, context):
    loader = yeti.ModuleLoader()
    loader.set_context(context)
    loader.add_fallback("resources.module_loader.module2")
    loader.add_fallback("resources.module_loader.module1")
    loader.load()
    context.run_for(.25)
    assert loader.get_module().name == "ModuleUno"

def test_module_reload(yeti, context):
    loader = yeti.ModuleLoader()
    loader.set_context(context)
    loader.load("resources.module_loader.module1")
    context.run_for(.25)
    module = loader.get_module()
    assert module.tally == 0
    module.tally += 1
    assert module.tally == 1
    loader.reload()
    context.run_for(.25)
    module = loader.get_module()
    assert module.tally == 0

def test_module_unload(yeti, context):
    loader = yeti.ModuleLoader()
    loader.set_context(context)
    loader.load("resources.module_loader.module1")
    context.run_for(.25)
    assert len(context.loaded_modules) == 1
    assert loader.module_object is not None
    context.unload_module("ModuleUno")
    context.run_for(.25)
    assert len(context.loaded_modules) == 0
    #assert loader.module_object is None