from typing import List
import datetime
import traceback
import json
import socket
import requests
from IPython.core.magic import register_cell_magic
from IPython.display import display, HTML
from IPython import get_ipython

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class JupyterSlackNotifier:
    """
    Jupyter Notebook Slack Notifier
    
    Usage:
        # Initialize at the beginning of your notebook
        notifier = JupyterSlackNotifier(
            webhook_url="your_webhook_url",
            channel="#your-channel",
            user_mentions=["<@USER_ID>"]  # Optional
        )
        
        # Then use the cell magic in any cell you want to monitor
        %%notify_slack
        # Your code here
        result = train_model()
    """
    
    _instance = None
    
    def __init__(self, webhook_url: str, channel: str, user_mentions: List[str] = []):
        """
        Initialize the Slack notifier for Jupyter notebooks.
        
        Parameters:
        -----------
        webhook_url : str
            The webhook URL to access your slack room.
            Visit https://api.slack.com/incoming-webhooks#create_a_webhook for more details.
        channel : str
            The slack room to log.
        user_mentions : List[str], optional
            Optional users ids to notify.
            Visit https://api.slack.com/methods/users.identity for more details.
        """
        self.webhook_url = webhook_url
        self.channel = channel
        self.user_mentions = user_mentions
        self.host_name = socket.gethostname()
        
        # Set as the active instance for the magic command
        JupyterSlackNotifier._instance = self
        
        # Register the cell magic
        self._register_magic()
        
        print("✓ Slack notifier initialized! Use %%notify_slack at the top of cells you want to monitor.")
    
    def _register_magic(self):
        """Register the cell magic command"""
        @register_cell_magic
        def notify_slack(line, cell):
            """
            Cell magic to send Slack notifications when a cell finishes running.
            
            Usage:
                %%notify_slack
                # Your code here
            """
            if JupyterSlackNotifier._instance is None:
                display(HTML('<span style="color: red;">Error: JupyterSlackNotifier not initialized!</span>'))
                return
            
            notifier = JupyterSlackNotifier._instance
            start_time = datetime.datetime.now()
            cell_id = f"Cell executed at {start_time.strftime(DATE_FORMAT)}"
            
            # Send start notification
            notifier._send_start_notification(cell_id, start_time)
            
            # Get the IPython instance to access the user namespace
            ipython = get_ipython()
            
            try:
                # Execute the cell code in the user's namespace
                ipython.run_cell(cell)
                
                # Send success notification
                end_time = datetime.datetime.now()
                elapsed_time = end_time - start_time
                notifier._send_success_notification(cell_id, start_time, end_time, elapsed_time)
                
            except Exception as ex:
                # Send error notification
                end_time = datetime.datetime.now()
                elapsed_time = end_time - start_time
                notifier._send_error_notification(cell_id, start_time, end_time, elapsed_time, ex)
                raise ex
    
    def _send_start_notification(self, cell_id: str, start_time: datetime.datetime):
        """Send notification when cell execution starts"""
        contents = [
            'Your cell execution has started 🎬',
            f'Machine name: {self.host_name}',
            f'Cell: {cell_id}',
            f'Starting date: {start_time.strftime(DATE_FORMAT)}'
        ]
        
        if self.user_mentions:
            contents.append(' '.join(self.user_mentions))
        
        dump = {
            "username": "Knock Knock",
            "channel": self.channel,
            "icon_emoji": ":clapper:",
            "text": '\n'.join(contents)
        }
        
        try:
            requests.post(self.webhook_url, json.dumps(dump))
        except Exception as e:
            print(f"Warning: Failed to send start notification: {e}")
    
    def _send_success_notification(self, cell_id: str, start_time: datetime.datetime, 
                                   end_time: datetime.datetime, elapsed_time: datetime.timedelta):
        """Send notification when cell execution completes successfully"""
        contents = [
            "Your cell execution is complete 🎉",
            f'Machine name: {self.host_name}',
            f'Cell: {cell_id}',
            f'Starting date: {start_time.strftime(DATE_FORMAT)}',
            f'End date: {end_time.strftime(DATE_FORMAT)}',
            f'Execution duration: {str(elapsed_time)}'
        ]
        
        if self.user_mentions:
            contents.append(' '.join(self.user_mentions))
        
        dump = {
            "username": "Knock Knock",
            "channel": self.channel,
            "icon_emoji": ":tada:",
            "text": '\n'.join(contents)
        }
        
        try:
            requests.post(self.webhook_url, json.dumps(dump))
        except Exception as e:
            print(f"Warning: Failed to send success notification: {e}")
    
    def _send_error_notification(self, cell_id: str, start_time: datetime.datetime,
                                 end_time: datetime.datetime, elapsed_time: datetime.timedelta,
                                 exception: Exception):
        """Send notification when cell execution crashes"""
        contents = [
            "Your cell execution has crashed ☠️",
            f'Machine name: {self.host_name}',
            f'Cell: {cell_id}',
            f'Starting date: {start_time.strftime(DATE_FORMAT)}',
            f'Crash date: {end_time.strftime(DATE_FORMAT)}',
            f'Crashed execution duration: {str(elapsed_time)}\n',
            "Here's the error:",
            f'{exception}\n',
            "Traceback:",
            f'{traceback.format_exc()}'
        ]
        
        if self.user_mentions:
            contents.append(' '.join(self.user_mentions))
        
        dump = {
            "username": "Knock Knock",
            "channel": self.channel,
            "icon_emoji": ":skull_and_crossbones:",
            "text": '\n'.join(contents)
        }
        
        try:
            requests.post(self.webhook_url, json.dumps(dump))
        except Exception as e:
            print(f"Warning: Failed to send error notification: {e}")
