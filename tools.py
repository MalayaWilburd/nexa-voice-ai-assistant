import logging #logging so we can see the output of the tools
from livekit.agents import function_tool, RunContext
import requests #need this for the funcion tool to make HTTP requests
from langchain_community.tools import DuckDuckGoSearchRun #this is our tool for searching the web
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional # Add this for Optional

@function_tool()

async def get_weather(
        context: RunContext, # type: ignore
        city: str) -> str: #passing a parameter called city and the API will recognize and it will return the weather for that city
    """
    Get the current weather for a given city.
    """

    try:
        # Make a request to the weather API
        response = requests.get(
            f"http://wttr.in/{city}?format=3") #passing city to API call
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather data for {city}."
        
    except Exception as e:
        logging.error(f"Error fetching weather data: {e}")
        return f"An error occurred while fetching the weather for {city}."

@function_tool()


async def search_web(
        context: RunContext, # type: ignore
        query: str) -> str: #passing a query parameter, it's basically a search query for the DuckDuckGo search tool
    """
    Search the web using DuckDuckGo.
    """
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query) #passing the query to the DuckDuckGo search tool
        logging.info(f"Search results for '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error searching the web: {e}")
        return f"An error occurred while searching the web for '{query}'."
    
    
@function_tool()

async def send_email(
        context: RunContext, # type: ignore
        to_email: str,
        subject: str,
        message: str,
        cc_email: Optional[str] = None
    ) -> str:
        """
        Send an email through Gmail SMTP.

        Args:
        - to_email (str): Recipient's email address.
        - subject (str): Subject of the email.
        - message (str): Body of the email. 
        - cc_email (Optional[str]): CC email address, if any.
        """
        try:
            # gmail SMTP configuration
            smpt_server = "smtp.gmail.com"
            smtp_port = 587

            # get credentials from environment variables
            gmail_user = os.getenv("GMAIL_USER")
            gmail_password = os.getenv("GMAIL_PASSWORD") # use app password for better security

            if not gmail_user or not gmail_password:
                logging.error("Gmail credentials are not set in environment variables.")
                return "Email sending failed: Gmail credentials are not set."
            
            # create message
            msg = MIMEMultipart()
            msg['From'] = gmail_user
            msg['To'] = to_email
            msg['Subject'] = subject

            # add CC if provided
            recipients = [to_email]
            if cc_email:
                msg['Cc'] = cc_email
                recipients.append(cc_email)

            # attach message body
            msg.attach(MIMEText(message, 'plain'))

            # connect to Gmail SMTP server
            server = smtplib.SMTP(smpt_server, smtp_port)
            server.starttls()  # secure the connection, enable TLS encryption
            server.login(gmail_user, gmail_password)  # login to the Gmail account

            # send email
            text = msg.as_string()
            server.sendmail(gmail_user, recipients, text)
            server.quit()  # close the connection

            logging.info(f"Email sent to {to_email} with subject '{subject}'")
            return f"Email sent to {to_email} with subject '{subject}'"   
        
        except smtplib.SMTPAuthenticationError:
            logging.error("Gmail authentication failed.")
            return "Email sending failed: Authentication error. Please check your Gmail credentials."
        except smtplib.SMTPAuthenticationError as e:
            logging.error(f"SMTP error occurred: {e}")
            return f"Email sending failed: {e}"
        except Exception as e:
            logging.error(f"An error occurred while sending email: {e}")
            return f"Email sending failed: {e}"