import yeti


class ArcadeDrive(yeti.Controller):

    def __init__(self):
        self.left_talon = yeti.get_controller("left_cim_talon")
        self.right_talon = yeti.get_controller("right_cim_talon")

    def bind(self, binder):
        self.binder = binder
        self.left_talon.bind(self)
        self.right_talon.bind(self)

    def set(self, x_axis, y_axis):
        if self.binder is None:
            raise Exception("set() was called on an unbound controller!")
        self.left_talon.set(x_axis + y_axis)
        self.right_talon.set(x_axis - y_axis)

    def free(self):
        self.binder = None
        self.left_talon.free()
        self.right_talon.free()


