class StaticClass {


    static function firstFunction() {
        debug("RUNNING");
		this.saludo();
	}

	static function saludo() {
		debug("HOLA!");
	}

	function exit() {
		debug("BYE");
	}
}