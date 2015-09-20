import asyncio
from os.path import join

def test_module_run(yeti, engine):
    class TestMod(yeti.Module):
        ran = False
        ran1 = False

        def module_init(self):
            self.ran = True

        @asyncio.coroutine
        @yeti.autorun
        def other_coro(self):
            self.ran1 = True
    engine.thread_coroutine(engine.start_module("test", mod_class=TestMod))
    engine.run_for(.25)
    mod = engine.get_module("test")
    assert mod.ran
    assert mod.ran1

def test_module_load(engine):
    engine.thread_coroutine(engine.start_module("resources.engine.module1"))
    engine.run_for(.25)
    mod = engine.get_module("resources.engine.module1")
    assert mod.name == "ModuleUno"

def test_module_fallback(engine):
    engine.module_sets["testmodset"] = ["resources.engine.module2", "resources.engine.module1"]
    engine.thread_coroutine(engine.start_module("testmodset"))
    engine.run_for(.25)
    mod = engine.get_module("testmodset")
    assert mod.name == "ModuleUno"

def test_config_load(engine, resources_dir):
    engine.load_config(join(resources_dir, "engine", "test.yml"))
    engine.run_for(.25)
    mod = engine.get_module("module1")
    assert mod.name == "ModuleUno"
    assert len(engine.enabled_modules) == 2
    assert len(engine.running_modules) == 1
    assert "resources.engine" in engine.module_dirs
    assert "testmods" in engine.module_sets
