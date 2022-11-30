# Deployment

## Heroku Production

1. Put into maintenance mode 

	```sh
	heroku maintenance:on --app spotlit
	```

1. Push to master on Heroku repository.

1. Run migrations if necessary.

	```sh
	heroku run python spotlit_due_diligence/manage.py migrate
	```

1. Turn off maintenance.

	```sh
	heroku maintenance:off --app spotlit

	```

## Heroku Staging/test

To deploy a branch to staging or test environment, run the following.

	```sh
	git push <repo name> <local branch name>:master -f
	```
	

## Configuring Celery Beat

When changin the crontab for a periodic task in the admin console, you must resave the tasks for the new schedule to take effect.