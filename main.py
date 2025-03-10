import datetime

from flask import Flask, render_template
app = Flask(__name__)

from google.cloud import datastore

datastore_client = datastore.Client()

def store_time(dt):
    entity = datastore.Entity(key=datastore_client.key("visit"))
    entity.update({"timestamp": dt})

    datastore_client.put(entity)


def fetch_times(limit):
    query = datastore_client.query(kind="visit")
    query.order = ["-timestamp"]

    times = query.fetch(limit=limit)

    return times

def delete_old_entries():
    five_minutes_ago = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(minutes=2)
    query = datastore_client.query(kind="visit")
    query.add_filter("timestamp", "<", five_minutes_ago)
    old_entries = query.fetch()

    for entry in old_entries:
        datastore_client.delete(entry.key)

@app.route("/")
def root():

    delete_old_entries()

    # Store the current access time in Datastore.
    store_time(datetime.datetime.now(tz=datetime.timezone.utc))

    # Fetch the most recent 10 access times from Datastore.
    times = fetch_times(10)

    return render_template("index.html", times=times)



if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)