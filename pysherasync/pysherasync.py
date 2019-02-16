## Created by Akshay araa47 
import asyncio 
import websockets 
import json 
import logging 
import hashlib
import hmac 
import logging 

VERSION = '0.6.0'

class PusherAsyncClient(object):
	host = "ws.pusherapp.com"
	client_id = "PusherAsyncClients"
	protocol = 6
	
	def __init__(self, key, cluster="", secure=True, secret="", user_data=None, log_level=logging.INFO,
				port=443, custom_host="", **loop_kwargs):
		
		#  """    Initialize the Pusher instance.
		# :param str or bytes key:
		# :param str cluster:
		# :param bool secure:
		# :param bytes or str secret:
		# :param Optional[Dict] user_data:
		# :param str log_level:
		# :param int port:
		# :param str custom_host:
		# :param Any loop_kwargs:"""
		if cluster:
			self.host = "ws-{cluster}.pusher.com".format(cluster=cluster)
		else:
			self.host = "ws.pusherapp.com"
		self.key = key
		self.secret = secret
		self.user_data = user_data or {}
		self.channels = {}
		self.url = self._build_url(secure, port, custom_host)
		self.websocket = None 
		self.logger = logging.getLogger(self.__module__)  # create a new logger

	@property
	def key_as_bytes(self):
		return self.key if isinstance(self.key, bytes) else self.key.encode('UTF-8')

	@property
	def secret_as_bytes(self):
		return self.secret if isinstance(self.secret, bytes) else self.secret.encode('UTF-8')

	async def connect(self, loop=None):
		self.logger.debug("Connecting to: %s"%(self.url))
		try:
			self.websocket = await websockets.connect(self.url, ssl=True, loop=loop, ping_interval=5, ping_timeout=5, close_timeout=5)
		except Exception as e:
			self.logger.error("Exception: def connect(self) Err: %s"%(e))

		return self.websocket
	
	async def disconnect(self):
		try:
			await self.websocket.close()
		except Exception as e:
			self.logger.error("Exception: def disconnect(self) Err:%s"%(e))
	

	async def subscribe(self, channel_name, event_name='pusher:subscribe', auth=None):
		"""Subscribe to a channel.
		:param str channel_name: The name of the channel to subscribe to.
		:param str auth: The token to use if authenticated externally.
		:rtype: pysher.Channel
		"""
		data = {'channel': channel_name}
		if auth is None:
			if channel_name.startswith('presence-'):
				data['auth'] = self._generate_presence_token(channel_name)
				data['channel_data'] = json.dumps(self.user_data)
			elif channel_name.startswith('private-'):
				data['auth'] = self._generate_auth_token(channel_name)
		else:
			data['auth'] = auth

		event = {'event': event_name, 'data': data}
		if channel_name:
			event['channel'] = channel_name
		msg = json.dumps(event)

		resp = None 
		try:
			await self.websocket.send(msg)
			resp = await self.websocket.recv()
			resp = json.loads(resp)
		except Exception as e:
			self.logger.error("Exception: def subscribe(self, channel_name=%s, auth=%s) Err:%s"%(channel_name, auth, e))
		
	  
		return resp 

	def _generate_presence_token(self, channel_name):
		"""Generate a presence token.
		:param str channel_name: Name of the channel to generate a signature for.
		:rtype: str
		"""
		subject = "{}:{}:{}".format(self.connection.socket_id, channel_name, json.dumps(self.user_data))
		h = hmac.new(self.secret_as_bytes, subject.encode('utf-8'), hashlib.sha256)
		auth_key = "{}:{}".format(self.key, h.hexdigest())

		return auth_key

	def _generate_auth_token(self, channel_name):
		"""Generate a token for authentication with the given channel.
		:param str channel_name: Name of the channel to generate a signature for.
		:rtype: str
		"""
		subject = "{}:{}".format(self.connection.socket_id, channel_name)
		h = hmac.new(self.secret_as_bytes, subject.encode('utf-8'), hashlib.sha256)
		auth_key = "{}:{}".format(self.key, h.hexdigest())

		return auth_key
	def _build_url(self, secure=True, port=None, custom_host=None):
		path = "/app/{}?client={}&version={}&protocol={}".format(
			self.key, self.client_id, VERSION, self.protocol
		)

		proto = "wss" if secure else "ws"

		host = custom_host or self.host
		if not port:
			port = 443 if secure else 80

		return "{}://{}:{}{}".format(proto, host, port, path)


