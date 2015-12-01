all: lint update push
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
