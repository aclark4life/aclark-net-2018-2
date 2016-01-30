all: commit-update push
db: migrate
lint: yapf flake wc
push: push-origin

project = aclarknet
app = database

clean: clean-postgres
clean-migrations:
	rm -rf $(project)/$(app)/migrations
clean-postgres:
	-dropdb $(project)
	-createdb $(project)
clean-sqlite:
	-rm -f db.sqlite3
	-git add db.sqlite3
commit:
	git commit -a
commit-update:
	git commit -a -m "Update"
copy:
	heroku maintenance:on
	heroku ps:scale web=0
	heroku pg:copy DATABASE_URL `heroku config:get DATABASE_URL2`
	heroku ps:scale web=1
	heroku maintenance:off
flake:
	-flake8 $(project)/*.py
	-flake8 $(project)/$(app)/*.py
install:
	virtualenv .
	bin/pip install -r requirements.txt
migrate:
	python manage.py migrate
migrations:
	python manage.py makemigrations $(app)
push-heroku:
	git push heroku
push-origin:
	git push
review:
	open -a "Sublime Text 2" `find $(project) -name \*.py | grep -v __init__.py` `find $(project) -name \*.html`
reset-db2:
	heroku pg:reset DATABASE_URL
serve:
	python manage.py runserver
start:
	-mkdir -p $(project)/$(app)
	-django-admin startproject $(project) .
	-django-admin startapp $(app) $(project)/$(app)
su:
	python manage.py createsuperuser
test:
	python manage.py test
wc:
	wc -l $(project)/*.py
	wc -l $(project)/$(app)/*.py
yapf:
	-yapf -i -e $(project)/urls.py $(project)/*.py
	-yapf -i $(project)/$(app)/*.py
