# GitHub Webhook Server

A simple Flask server to handle GitHub webhooks, pull updates, and restart `myapp.service`.

## Setup

1. **Install Dependencies**:
   ```bash
   source myenv/bin/activate
   pip install GitPython
   ```

2. **Run Server**:
    ```bash
    python3 webhook_server.py
    ```

## Test Webhook

To test the webhook:

    ```bash
    curl -X POST http://<server-ip>:3000/webhook \
        -H "Content-Type: application/json" \
        -d '{"ref": "refs/heads/main", "repository": {"name": "my-repo"}}'
    ```

## Notes

Used tailscale to get public dns.

    ```bash
    sudo tailscale funnel 3000
    ```

The script is currently running in a different location to let git pull update the files(??)
