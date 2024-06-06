import asyncio
import websockets
import ssl

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile="/home/sadmin/chatbot/newsumabot/src/sumasoft.com.pem", keyfile="/home/sadmin/chatbot/newsumabot/src/sumasoft_key.pem")

async def echo(websocket, path):
    async for message in websocket:
        await websocket.send(message)

start_server = websockets.serve(echo, "192.168.100.37", 7890, ssl=ssl_context)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
