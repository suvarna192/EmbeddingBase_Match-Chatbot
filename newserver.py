import websockets
import asyncio
import threading
import logging
import http.server
import socketserver
import os
import signal
from faqengine import FaqEngine

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ports
PORT = 7890
HTTP_PORT = 8001

logger.info("Server listening on Port %d", PORT)

# Data structures for sessions and states
sessions = {}
context = {}
dialogue_state = {}

# Predefined guided flow responses
guided_flow = {
    "webinar enquire": {
        "greetings": "Welcome to Sumasoft. How may I help you?",
        "Information": "Thanks for sharing your details.",
        "Acknowledgement": "Thank you for contacting Sumasoft Pvt. Ltd."
    },
    "service line Enquire": {
        "greetings": "Welcome to Sumasoft. How may I help you?",
        "Information": "Thanks for sharing your details.",
        "Acknowledgement": "Thank you for contacting Sumasoft Pvt. Ltd."
    }
}

# Flag for HTTP server running state
http_server_running = True

# Setup logging for a specific session
def setup_logging(session_id):
    log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_file = os.path.join(log_directory, f"{session_id}.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger = logging.getLogger(session_id)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

# Setup logging for errors
def setup_error_logging():
    error_log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    if not os.path.exists(error_log_directory):
        os.makedirs(error_log_directory)
    error_log_file = os.path.join(error_log_directory, "error.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler(error_log_file)
    handler.setFormatter(formatter)
    error_logger = logging.getLogger("error_logger")
    error_logger.addHandler(handler)
    error_logger.setLevel(logging.ERROR)
    return error_logger

# Error logger
error_logger = setup_error_logging()

# WebSocket echo handler
async def echo(websocket, path):
    session_id = str(id(websocket))
    sessions[session_id] = websocket
    session_logger = setup_logging(session_id)
    context[session_id] = []
    dialogue_state[session_id] = ""
    logger.info("A client connected with session ID: %s", session_id)
    
    try:
        async for message in websocket:
            session_logger.info(f"User: {message}")
            context[session_id].append(message)
            response, _class = faq_model.query(message)
            
            if _class not in ('Acknowledgement', 'greetings', 'Information', 'OutOfScope', 'Exception'):
                if _class not in ('job enquiry', 'Company Enquire', 'Tech support enquire', 'Employee Enquire'):
                    dialogue_state[session_id] = _class

            if response == "Could not understand your query. Please rephrase it again":
                error_message = f"Session ID: {session_id} - User Query: {message}"
                session_logger.info(f"Bot: {response}")
                error_logger.error(error_message)
                await websocket.send(response)
                context[session_id].append(response)
            else:
                if _class in ('Acknowledgement', 'greetings', 'Information') and dialogue_state[session_id] != "":
                    response = guided_flow[dialogue_state[session_id]][_class]
                
                session_logger.info(f"Bot: {response}")
                await websocket.send(response)
                context[session_id].append(response)
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"A client with session ID {session_id} disconnected")
    finally:
        del sessions[session_id]
        session_logger.handlers.clear()

# Serve HTML files using a simple HTTP server
def serve_html():
    global http_server_running
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", HTTP_PORT), Handler)
    logger.info("Serving HTML file at http://0.0.0.0:%d/client.html", HTTP_PORT)
    while http_server_running:
        httpd.handle_request()

# Start the WebSocket server
start_server = websockets.serve(echo, "0.0.0.0", PORT)

# Start the HTML server in a separate thread
html_thread = threading.Thread(target=serve_html)
html_thread.start()

# Setup the FAQ engine
base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
faqs_list = [
    os.path.join(base_path, "Greetings.csv"),
    os.path.join(base_path, "sumasoft.csv"),
    os.path.join(base_path, "Information.csv"),
    os.path.join(base_path, "Acknowledgement.csv")
]
faq_model = FaqEngine(faqs_list, "sentence-transformers")

# Run the asyncio event loop
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
