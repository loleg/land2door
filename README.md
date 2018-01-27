Land2Door
=====================

Build data on producers & open this information to consumers to develop the direct selling model in Switzerland.

https://hack.opendata.ch/project/141

This project is open source under the [MIT License](LICENSE.md). It was made with [Blemmy](https://github.com/datalets/blemmy), a headless CMS based on [Wagtail](https://wagtail.io).

# Development environment

The easiest way to set up your machine would be to use [Vagrant](https://vagrantup.com), then in the project folder in the terminal type: `vagrant up`. Then when it is ready, follow instructions for *Database setup*.

To set up a full development environment, follow all these instructions.

**Backend setup**

If not using Vagrant: after installing Python 3, from the project folder, deploy system packages and create a virtual environment as detailed (for Ubuntu users) below:

```
sudo apt-get install python3-venv python3-dev libjpeg-dev

pyvenv env
. env/bin/activate

pip install -U pip
pip install -r requirements.txt
```

At this point your backup is ready to be deployed.

## Database setup

Once your installation is ready, you can get a blank database set up and add a user to login with.

If you are using Vagrant, enter the shell of your virtual machine now with `vagrant ssh`

Run these commands:

```
./manage.py migrate
./manage.py createsuperuser
```

You will be asked a few questions to create an administrator account.

**Starting up**

If you have one installed, also start your local redis server (`service redis start`).

After completing setup, you can use:

```
./manage.py runserver
```

(In a Vagrant shell, just use `djrun`)

Now access the admin panel with the user account you created earlier: http://localhost:8000/admin/

## Data backups

Issues with migrating database tables in SQLite during development? Try `./manage.py migrate --fake`

For development, it's handy to have access to a copy of the production data. To delete your local database and restore from a file backup, run:

```
rm blemmy-dev.sqlite3
python manage.py migrate
python manage.py loaddata blemmy.home.json
```

You might want to `createsuperuser` again at this point.

# Contributing

It is very easy to contribute. You can fork this repo and send a pull request. Make sure to add your name to contributors.txt. Try to submit an issue to discuss your modifications before the pull request so we can see if they are inline with the project's goals.

You can also open an issue for a feature request or architecture suggestion.

You can also check out the code for any _TODO_ comments.

## Development directions

- create a "starter template" ([example](https://github.com/petertait/react-kirby-starter))
- add a GraphQL query API.
- add support for Puput's blog models.
- add other new model types and serialisers (check [Django REST Framework](http://www.django-rest-framework.org/) docs for how to do this. It's easy.), looking at other headless CMS designs for inspiration or standards.
- allow creation of new pages by POSTing JSON data to the correct endpoint.

## More links

This project is inspired and aims to reference and collaborate with these projects:

- https://github.com/tomchristie/apistar
- https://github.com/FFX01/pager
- https://github.com/directus/directus
- https://github.com/aya-experience/citation

For more information on this types of application, visit:

- https://jamstack.org/
- https://headlesscms.org
- https://dadi.tech/en/web/
- https://www.cyon.ch/blog/Headless-CMS

### Why Blemmy

[Wikipedia knows](https://en.wikipedia.org/w/index.php?title=Blemmy&redirect=no).
