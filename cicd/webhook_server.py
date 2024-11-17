# pylint: disable=C0114
# pylint: disable=import-error

import subprocess
import git
from git.exc import GitError
from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle incoming webhook POST requests.

    This function verifies the request method, pulls the latest changes from the Git repository,
    restarts the application service, and returns an appropriate response.
    """
    if request.method == 'POST':
        try:
            repo = git.Repo('/home/ish/co2-sensor-script')
            origin = repo.remotes.origin
            origin.pull()

            subprocess.run(["sudo", "systemctl", "restart", "myapp.service"], check=True)

            return "Webhook received and application restarted!", 200
        except (GitError, subprocess.CalledProcessError) as e:
            print(f"Error: {e}")
            return "Error processing the webhook.", 500
    else:
        abort(400)
        return "Bad Request", 400  # Added return statement to satisfy pylint

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
