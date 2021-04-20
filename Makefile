COPYRIGHT_HOLDER="涂紳騰(Shen-Teng Tu)"

.PHONY: format babel-extract

format:
	@black ./
	@prettier --write .

babel-extract:
	@pipenv run python setup.py extract_messages \
			-F babel.cfg \
			--copyright-holder $(COPYRIGHT_HOLDER) \
			-o locale/py_sms_impl.pot \
			--input-dirs web
