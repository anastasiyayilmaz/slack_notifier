from typing import List
import datetime
import traceback
import json
import socket
import requests
from IPython.core.magic import register_cell_magic
from IPython.display import display, HTML
from IPython import get_ipython
from io import StringIO
import sys

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
            
            # Send start notification with the cell code
            notifier._send_start_notification(cell, start_time)
            
            # Get the IPython instance to access the user namespace
            ipython = get_ipython()
            
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            cell_result = None
            
            try:
                # Execute the cell code in the user's namespace
                result = ipython.run_cell(cell)
                
                # Get the output
                output = captured_output.getvalue()
                
                # Get the result value if there is one
                if result.result is not None:
                    cell_result = result.result
                
                # Restore stdout
                sys.stdout = old_stdout
                
                # Print the output so it still shows in the notebook
                if output:
                    print(output, end='')
                
                # Send success notification with output
                end_time = datetime.datetime.now()
                elapsed_time = end_time - start_time
                notifier._send_success_notification(cell_id, start_time, end_time, elapsed_time, output, cell_result)
                
            except Exception as ex:
                # Restore stdout
                sys.stdout = old_stdout
                
                # Get any output that was produced before the error
                output = captured_output.getvalue()
                if output:
                    print(output, end='')
                
                # Send error notification
                end_time = datetime.datetime.now()
                elapsed_time = end_time - start_time
                notifier._send_error_notification(cell_id, start_time, end_time, elapsed_time, ex, output)
                raise ex
    
    def _send_start_notification(self, cell_id: str, start_time: datetime.datetime):
        """Send notification when cell execution starts"""
        contents = [
            'The cell is running.',
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
                                   end_time: datetime.datetime, elapsed_time: datetime.timedelta,
                                   output: str = "", cell_result=None):
        """Send notification when cell execution completes successfully"""
        contents = [
            "The cell is done.",
            f'Cell: {cell_id}',
            f'Starting date: {start_time.strftime(DATE_FORMAT)}',
            f'End date: {end_time.strftime(DATE_FORMAT)}',
            f'Execution duration: {str(elapsed_time)}'
        ]
        
        # Add output if present (truncate if too long for Slack)
        if output:
            output_preview = output[:2000] + "..." if len(output) > 2000 else output
            contents.append(f'\nCell Output:\n```\n{output_preview}\n```')
        
        # Add return value if present
        if cell_result is not None:
            try:
                result_str = str(cell_result)
                if len(result_str) > 500:
                    result_str = result_str[:500] + "..."
                contents.append(f'\nReturn Value: {result_str}')
            except:
                contents.append('\nReturn Value: <unable to stringify>')
        
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
                                 exception: Exception, output: str = ""):
        """Send notification when cell execution crashes"""
        contents = [
            "The cell has crashed ☠️",
            f'Cell: {cell_id}',
            f'Starting date: {start_time.strftime(DATE_FORMAT)}',
            f'Crash date: {end_time.strftime(DATE_FORMAT)}',
            f'Crashed execution duration: {str(elapsed_time)}\n'
        ]
        
        # Add any output that was produced before the error
        if output:
            output_preview = output[:1000] + "..." if len(output) > 1000 else output
            contents.append(f'Output before error:\n```\n{output_preview}\n```\n')
        
        contents.extend([
            "Here's the error:",
            f'{exception}\n',
            "Traceback:",
            f'```\n{traceback.format_exc()}\n```'
        ])
        
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
