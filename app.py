from flask import Flask, request, redirect, url_for, abort, render_template
import requests
import yaml
app = Flask(__name__)

with open('settings.yaml', encoding='utf8') as file:
    conf = yaml.load(file)


@app.route("/")
def root():
    # This is a work-around the fact that we cannot grab the GET parameters
    # since they are stuck behind the hash (#), thus being kept in the browser
    # and not sent to us. We solve this by running some JavaScript which is
    # able to grab those client-side values and redirect so they can be
    # processed server-side.
    return '''<!-- Yes, this is stupid --><script type="text/javascript">
    // Credit goes to http://stackoverflow.com/a/7866932
    // Gather the URL
    var url = window.location.href;
    var splitted_url = url.split("?");
    var new_url = null;
    // Was there a question mark present?
    if (splitted_url.length == 2) {
        // Yes, redirect in a way that makes the GET parameters accessible
        // on the server
        var params = splitted_url[1];
        new_url = "/play/?" + params;
    } else {
        // No, just redirect to the server with no parameters
        new_url = "/play/";
    }
    // Do the actual redirect
    window.location = new_url;
</script>
<noscript>Du må aktivere Javascript for å lytte til episodene.</noscript>
<p>Omdirigerer, vennligst vent…</p>'''


@app.route("/play/")
def play():
    show_id = None
    episode_id = None

    if 'showID' in request.args:
        try:
            show_id = int(request.args['showID'])
        except ValueError:
            abort(400)
            return

    if 'broadcastID' in request.args:
        try:
            episode_id = int(request.args['broadcastID'])
        except ValueError:
            abort(400)
            return

    show_id_present = show_id is not None
    episode_id_present = episode_id is not None
    if show_id_present and episode_id_present:
        r = requests.get(conf['radio-rest-api'] + "/v2/lyd/ondemand/{}/{}"
                             .format(show_id, episode_id))
        r.raise_for_status()
        episode_data = r.json()
        if not "url" in episode_data:
            # Assuming empty response, thus these IDs are not found
            abort(404)
            return

        return render_template('play.html', episode=episode_data)
    else:
        abort(404)
        return
