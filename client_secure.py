import asyncio
import ssl
import websockets

# Load SSL context with CA certificate for server verification
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# ssl_context.load_verify_locations("/home/sadmin/chatbot/newsumabot/src/sumasoft.com.pem")

# Create SSL context
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# ssl_context.load_cert_chain(certfile="/home/sadmin/chatbot/newsumabot/src/sumasoft.com.pem", keyfile="/home/sadmin/chatbot/newsumabot/src/sumasoft_key.pem")


# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# # localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
# certfile_path = "/home/sadmin/chatbot/newsumabot/src/sumasoft.com.pem"
# keyfile_path = "/home/sadmin/chatbot/newsumabot/src/sumasoft_key.pem"
# ssl_context.load_verify_locations(certfile=certfile_path, keyfile=keyfile_path)

# Create an SSL context for client-side connection
certfile_path = "/home/sadmin/chatbot/newsumabot/src/sumasoft.com.pem"
ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=certfile_path)
ssl_context.check_hostname = False  # Set to True if hostname verification is required
ssl_context.verify_mode = ssl.CERT_NONE  # Change this to ssl.CERT_REQUIRED for production


async def hello():
    uri = "wss://192.168.100.37:7890"
    async with websockets.connect(uri,ssl=ssl_context) as websocket:
        name = input("Enter your message: ")

        await websocket.send(name)
        print(f">>> {name}")

        greeting = await websocket.recv()
        print(f"<<< {greeting}")

if __name__ == "__main__":
    asyncio.run(hello())
