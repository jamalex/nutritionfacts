# nutritionfacts
The telemetry server for Kolibri installations.

# Deploying

## Prerequisites

Nutritionfacts is deployed and run using Nanobox, a tool that unifies the dev
and production environments.

Install the Nanobox toolkit from [their
website](https://dashboard.nanobox.io/download).

Log in to your Nanobox account by running `nanobox login`.

## Development

Development should happen within the nanobox dev environment, which tries to
match the production environment as much as possible. 

Once you're in the root directory of the nutritionfacts repo, you can get a dev
environment set up by running `nanobox run`. This will:

1. Set up a Virtualbox VM and pull in all the scaffolding for running nanobox.
1. Pull in Docker and download all python dependencies
1. Drop you into a (docker) environment with all the dependencies you need to
   run the app.
   
First, set up a local DNS route to your dev server by running `nanobox dns add
local nutritionfacts.local`. You can then open `nutritionfacts.local` in your
browser and load the app from there, once you have the app started.
   
Once inside the app, you can start the server in dev mode by running `python
manage.py runserver 0.0.0.0:8000`.

Visit your running app by going to [](http://nutritionfacts.local:8000).

## Testing the app in "production mode"

To have a setup that's closer to production, then run the following:

```
nanobox deploy dry-run
```

This will bring up a 'production' setup hosted on your machine: it will bring up
separate containers for the database and the app, run the production app server
using `waitress`, and doesn't give you a shell off-the-bat (but still allows you
to get one).

Once you've successfully run the app, nanobox will print the app server in the
console. Visit the IP address on your browser to see the app in action.


## Deploying to production

Now that you've tested that the app is working, it's time to deploy it! First,
you need to associate the 'production' app to your local source code. Do that by
running:

```
nanobox remote add nutritionfacts
```

From there, you can deploy to production by running:

```
nanobox deploy nutritionfacts
```

This would upload your source code to nanobox, and then deployment will continue
on their servers.

## Miscellaneous

Q: What if I need to add more dependencies?

Just add them to requirements.txt, then restart your app or prod server. Nanobox
should automatically detect the change and install the new dependency.

Q: What if I need to add some setup code before the server is running?

Nanobox offers hooks for different parts of the app lifecycle. Start by looking
at this [django-specific docs
page](https://guides.nanobox.io/python/django/configure-django/).

Q: How can I see the app logs?

You can either run:

```
nanobox log nutritionfacts
```

Or visit the Nanobox app UI.


