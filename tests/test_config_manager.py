from os.path import join


def test_basic_parsing(yeti, resources_dir):
    config_manager = yeti.ConfigManager()
    config_manager.parse_config(join(resources_dir, "config_manager", "parsing.conf"))
    correct_config_structure = {"SectionA": ["a", "b", "c"], "SectionB": ["a", "b", "c"]}
    assert config_manager.config_structure == correct_config_structure


def test_module_loading(yeti, context, resources_dir):
    config_manager = yeti.ConfigManager()
    config_manager.parse_config(join(resources_dir, "config_manager", "basic.conf"))
    config_manager.load_startup_mods(context)
    context.run_for(.5)
    moda = config_manager.module_loaders["moda"]
    modb = config_manager.module_loaders["modb"]
    modc1 = config_manager.module_loaders["modc1"]
    assert moda.fallback_list == ["moda1", "moda2"]
    assert modb.fallback_list == ["modb"]
    assert modc1.fallback_list == ["modc1", "modc2"]