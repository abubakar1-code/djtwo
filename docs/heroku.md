
# Useful Commands in Heroku CLI

Turn maintenance mode on.

```sh
heroku maintenance:on --app spotlit
```

Turn maintenance mode off.

```sh
heroku maintenance:off --app spotlit
```

See logs.

```sh
heroku logs -t --app spotlit
```

Migrate the database. 

```sh
heroku run python spotlit_due_diligence/manage.py migrate
```
Open django shell.

```sh
heroku run python spotlit_due_diligence/manage.py shell --app spotlit
```

Open bash shell.

```sh
heroku run bash --app spotlit
```

Rollback changes.

```sh
heroku rollback —app spotlit
```

To deploy a branch to staging or test environment, run the following.

```sh
git push <repo name> <local branch name>:master -f
```