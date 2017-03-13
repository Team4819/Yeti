#include <yeti.h>

class Claw: public yeti::Controller {
private:
	Controller* talon_controller;
public:
	void bind(Controller* binder){
		binder = binder;
		talon_controller->bind(this*);
	}

	void set(bool closed){
		if (closed)
			talon_controller.set(1);
		else
			talon_controller.set(-1);
	}

	void free(){
		binder = NULL;
		talon_controller->free();
	}
};

static int main(char* args[]){

	return 0;
}
