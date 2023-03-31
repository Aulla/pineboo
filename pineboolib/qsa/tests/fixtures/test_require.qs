class ESArray {
	var a_

	function ESArray(init) {
		this.a_ = init || [];
	}

	static function from(a) {
		return new this(a);
	}

	function forEach(callback) {
		for (var i = 0; i < this.a_.length; i++) {
			callback(this.a_[i], i, this.a_)
		}
	}

	function map(callback) {
		const arr = new ESArray();
		for (var i = 0; i < this.a_.length; i++) {
			arr.push(callback(this.a_[i], i, this.a_));
		}
		return arr;
	}

	function filter(callback) {
		const arr = new ESArray();
		for (var i = 0; i < this.a_.length; i++) {
			if (callback(this.a_[i], i, this.a_)) {
				arr.push(this.a_[i]);
			}
		}
		return arr;
	}

	function find(callback) {
		for (var i = 0; i < this.a_.length; i++) {
			if (callback(this.a_[i], i, this.a_)) {
				return this.a_[i];
			}
		}
		return undefined;
	}

	function reduce(callback, init) {
		var res = init;
		for (var i = 0; i < this.a_.length; i++) {
			res = callback(res, this.a_[i]);
		}
		return res;
	}

	function every(callback) {
		for (var i = 0; i < this.a_.length; i++) {
			if (!callback(this.a_[i], i, this.a_)) {
				return false;
			}
		}
		return true;
	}

	function some(callback) {
		for (var i = 0; i < this.a_.length; i++) {
			if (callback(this.a_[i], i, this.a_)) {
				return true;
			}
		}
		return false;
	}

	function at(index) {
		const i = index < 0 ? this.a_.length - index : index;

		return this.a_[i];
	}

	function push(item) {
		return this.a_.push(item);
	}

	function toString() {
		return this.a_.toString();
	}

	function join(sep) {
		return this.a_.join(sep)
	}

	function get() {
		return this.a_;
	}
}

ESArray