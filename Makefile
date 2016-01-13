all: lint update push
db: clean migrate su
lint: yapf flake wc

project = aclarknet
app = database

clean:
	-rm -f db.sqlite3
	-git add db.sqlite3
	-dropdb $(project)
	-createdb $(project)
flake:
	-flake8 $(project)/*.py
	-flake8 $(project)/$(app)/*.py
update:
	git commit -a -m "Update"
push-github:
	git push
push-heroku:
	git push heroku
push: push-github
yapf:
	-yapf -i $(project)/*.py
	-yapf -i $(project)/$(app)/*.py
migrate:
	rm -rf $(project)/$(app)/migrations
	python manage.py makemigrations $(app)
	python manage.py migrate
review:
	open -a "Sublime Text 2" `find $(project) -name \*.py | grep -v __init__.py` `find $(project) -name \*.html`
start:
	-mkdir -p $(project)/$(app)
	-django-admin startproject $(project) .
	-django-admin startapp $(app) $(project)/$(app)
su:
	python manage.py createsuperuser
wc:
	wc -l $(project)/*.py
	wc -l $(project)/$(app)/*.py
backup:
	heroku pg:backups capture
copy:
	heroku maintenance:on
	heroku ps:scale web=0
	heroku pg:copy DATABASE_URL `heroku config:get DATABASE_URL2`
	heroku ps:scale web=1
	heroku maintenance:off
test:
	python manage.py test
reset:
	heroku pg:reset DATABASE_URL
heroku-remote:
	git remote add heroku git@heroku.com:aclarknet-database.git
heroku-remote2:
	git remote add heroku git@heroku.com:aclarknet-database2.git
