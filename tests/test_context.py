
def test_context_run(yeti, context):
    class SetterMod(yeti.Module):
        message = "..."

        def module_init(self):
            self.message = "Hi!"
            self.event_loop.stop()

    module = SetterMod()
    context.load_module(module)
    assert module.message == "..."
    context.run_forever()
    assert module.message == "Hi!"

def test_context_datastore(yeti, context):
    data_1 = context.get_interface_data("test 1")[0]
    data_2 = context.get_interface_data("test 2")[0]
    data_1["myval"] = True
    data_2["herval"] = "masterful!"
    assert data_1 != data_2
    assert context.get_interface_data("test 1")[0]["myval"] == True
    assert context.get_interface_data("test 2")[0]["herval"] == "masterful!"

