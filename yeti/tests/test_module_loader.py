def test_module_load(yeti):
    context = yeti.Context()
    loader = yeti.ModuleLoader()
    loader.set_context(context)
    loader.load("resources.module_loader.module1")
    context.run_for(.5)
    assert loader.get_module().name == "ModuleUno"

def test_module_fallback(yeti):
    context = yeti.Context()
    loader = yeti.ModuleLoader()
    loader.set_context(context)
    loader.load("resources.module_loader.module2")
    loader.add_fallback("resources.module_loader.module1")
    context.run_for(.5)
    assert loader.get_module().name == "ModuleUno"
