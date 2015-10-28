ip = 127.0.0.1
port = 8000
interface = wlan0
address = ifconfig $(interface) | grep "inet addr" | python -c "s=raw_input(); import re; print re.search('addr:(?P<ip>[\w\.]*)',s).group('ip')"

all:
	echo '$(shell $(address)):$(port)'
	python manage.py runserver $(shell $(address)):$(port)

db:
	touch db.sqlite3
	rm db.sqlite3
	python manage.py migrate

dbfill: db
	python populate_db.py

run:
	python manage.py runserver

test:
	python manage.py test -v 2

shell:
	python manage.py shell