from flask import Flask, request, abort
import git
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Verify that the request is from GitHub
    if request.method == 'POST':
        try:
            # Pull the latest code from the repository
            repo = git.Repo('/home/ish/co2-sensor-script')
            origin = repo.remotes.origin
            origin.pull()
            
            # Restart the service
            subprocess.run(["sudo", "systemctl", "restart", "myapp.service"], check=True)
            
            return "Webhook received and application restarted!", 200
        except Exception as e:
            print(f"Error: {e}")
            return "Error processing the webhook.", 500
    else:
        abort(400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
