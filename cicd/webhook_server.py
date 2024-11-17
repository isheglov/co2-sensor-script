# pylint: disable=C0114
# pylint: disable=W0718
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
        print("Received a POST request on /webhook endpoint.")
        try:
            print("Accessing the Git repository...")
            repo = git.Repo('/home/ish/co2-sensor-script')
            origin = repo.remotes.origin
            print("Pulling the latest changes from the remote repository...")
            origin.pull()
            print("Successfully pulled the latest changes.")

            # List of services to restart
            services = ["myapp.service", "co2_monitor.service", "co2sensor.service"]

            for service in services:
                print(f"Attempting to restart service: {service}")
                try:
                    # Execute the systemctl restart command
                    result = subprocess.run(
                        ["sudo", "systemctl", "restart", service],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True  # Ensures that output is returned as a string
                    )
                    print(f"Successfully restarted {service}.")
                    print(f"Standard Output: {result.stdout}")
                    print(f"Standard Error: {result.stderr}")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to restart {service}.")
                    print(f"Return Code: {e.returncode}")
                    print(f"Output: {e.output}")
                    print(f"Error: {e.stderr}")
                    # Optionally, you can choose to abort further restarts if one fails
                    # abort(500, description=f"Failed to restart {service}.")

            return "Webhook received and application restarted!", 200
        except GitError as e:
            print(f"Git error occurred: {e}")
            return "Error processing the webhook due to Git issues.", 500
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "An unexpected error occurred while processing the webhook.", 500
    else:
        print("Received a non-POST request on /webhook endpoint.")
        abort(400)
        return "Bad Request", 400  # Added return statement to satisfy pylint

if __name__ == '__main__':
    print("Starting the Flask webhook server...")
    app.run(host='0.0.0.0', port=3000)
