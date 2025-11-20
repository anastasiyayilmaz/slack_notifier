# Slack Notifier

A lightweight modification of [knockknock](https://github.com/huggingface/knockknock) tailored for Jupyter notebooks. It sends a Slack notification automatically when a cell finishes running.

Usage:

### 1.	Create a Slack webhook URL

Follow the steps in the [Slack documentation](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/#create_a_webhook). You’ll need to create a Slack app and configure where the messages should go (a specific channel or a direct message to yourself).

### 2. Initialize the notifier at the start of your notebook:

```ruby
from slack_sender import JupyterSlackNotifier
notifier = JupyterSlackNotifier(
    webhook_url="your_webhook_url", #add the webhook URL
    channel="#your-channel" #the name of your channel
)
```

### 3. Add the magic command to any cell you want to track:

```ruby
%%notify_slack
```
That’s it — once the cell finishes running, you’ll receive a Slack message.
