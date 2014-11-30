import yeti


class Example(yeti.Module):

    def module_init(self):
        self.add_task(self.say_hi("Hello world 1!"),  yeti.EventCondition("tick"))
        self.add_task(self.say_hi("Good-bye world 1!"), yeti.FallingEventCondition("tick"))

    def say_hi(self, message):
        i = 5
        while i > .5:
            print(message + "i=" + str(i))
            i -= .5
            if i < 4:
                raise Exception("Oops, this is a CRITICAL Error!")
            yield 1, yeti.EventCondition("tick")


def get_module():
    return Example
