.PHONY: format

format:
	@black ./
	@prettier --write .
	