all: lint update push
db: clean migrate su
lint: yapf flake wc
clean:
	-rm -f db.sqlite3
	-git add db.sqlite3
	-dropdb aclarknet
	-createdb aclarknet
flake:
	flake8 project/*.py
	flake8 project/app/*.py
update:
	git commit -a -m "Update"
push:
	git push
	git push heroku
yapf:
	yapf -i project/*.py
	yapf -i project/app/*.py
migrate:
	rm -rf project/app/migrations
	python manage.py makemigrations app
	python manage.py migrate
review:
	open -a "Sublime Text 2" `find project -name \*.py`
su:
	python manage.py createsuperuser
wc:
	wc -l project/*.py
	wc -l project/app/*.py
