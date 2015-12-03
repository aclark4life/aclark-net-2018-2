all: lint update push
db: migrate su
lint: yapf flake
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
	rm -f db.sqlite3
	rm -rf project/app/migrations
	python manage.py makemigrations app
	python manage.py migrate
	git add db.sqlite3
su:
	python manage.py createsuperuser
