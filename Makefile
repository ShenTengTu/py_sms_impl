COPYRIGHT_HOLDER="涂紳騰(Shen-Teng Tu)"
LOCALE_DIR=locale
MO_DOMAIN=py_sms_impl
POT_FILE=$(LOCALE_DIR)/$(MO_DOMAIN).pot

cmd_babel=babel-extract babel-init babel-compile
.PHONY: format $(cmd_babel) build_tailwind dl_po test dev_server

format:
	@black ./
	@prettier --write .

babel-extract:
	@pipenv run python setup.py extract_messages \
			-F babel.cfg \
			--copyright-holder $(COPYRIGHT_HOLDER) \
			-o $(POT_FILE) \
			--input-dirs web

babel-init:
ifdef locale
	@pipenv run python setup.py init_catalog \
			-i $(POT_FILE) \
			--output-dir $(LOCALE_DIR) \
			--locale $(locale) \
			-D $(MO_DOMAIN)
else
	@echo "Using : 'babel-init locale=en_US' "
endif

babel-compile:
ifdef locale
	@pipenv run python setup.py compile_catalog \
			--directory $(LOCALE_DIR) \
			--locale $(locale) \
			-D $(MO_DOMAIN)
else
	@echo "Using : 'babel-compile locale=en_US' "
endif

build_tailwind:
	@NODE_ENV=production \
			npx tailwindcss-cli@latest build ./assets/css/tailwind.css \
			-o ./web/static/css/tailwind.css

dl_po:
	@pipenv run dl_po

test:
	@pipenv run test

dev_server:
	@pipenv run dev_server

dump_sql_shema:
	@pipenv run python setup.py dump_sql_schema \
			--scheme postgresql \
			--driver psycopg2 \
			-o ./init_db/pg_init_db.sql
