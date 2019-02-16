PysherAsync 
=============

`pysherasync` is a python module for handling Pusher Channels. It is based on @ekulyk's `PythonPusherClient` and @nlsdfnbch  `Pysher`. This is a re-implementation of the project
to use more efficient asynchronous logic and more efficient websockets. A key difference is the dropped support for pre-3.5 Python versions. 

This is also currently a very minimalistic implementation and may be missing some components, please submit an issue and let me know if you run into any problems. 

Installation
------------

Simply clone the project and run `python setup.py install` - or install via pip `pip install pysherasync`.

This module depends on websockets module available from: <https://github.com/aaugustin/websockets>

Example
-------

Example of using this pusher client to consume websockets:

```python
import pysherasync

async def bitstamp_ob_subscription(loop):
    global loop 
    # This is your app key, currently set to https://www.bitstamp.net/websocket/ 
    appkey = "de504dc5763aeef9ff52"
    # Create an instance of PusherAsyncClient and pass it the appkey 
    pusherclient = pysherasync.PusherAsyncClient(appkey)
    # Connect to websocket 
    pushersocket = await pusherclient.connect()
    # Subscribe to channel 
    status = await pusherclient.subscribe(channel_name='order_book')
    print("Subscription Status: %s"%(status))
    while True:
        ## This is because re-connection logic is not implemented yet
        if not pushersocket.open:
            # on disconnections, reconnect
            print("Connection reconnecting")
            # re-connect
            pushersocket = await pusherclient.connect()
            # re-subscribe 
            status = await pusherclient.subscribe(channel_name='order_book')
            print("Subscription Status: %s"%(status))
        try:
            # wait for msg
            msg = await asyncio.wait_for(pushersocket.recv(), 5)
            # parse to json 
            msg = json.loads(msg)
            # print the msg 
            if msg:
                print(msg)        
        except asyncio.TimeoutError:
            print("asyncio timeout while waiting for ws msg")
        except Exception as e:
            print(e)

 if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bitstamp_ob_subscription(loop))
    loop.close()
```
    
Performance
------
PysherAsync relies on websockets which is one of the most efficient implementations on python.

Thanks
------
A big thanks to @ekulyk for developing the [PythonPusherClient](https://github.com/ekulyk/PythonPusherClient) library.

A big thanks to @nlsdfnbch for developing the [Pysher](https://github.com/nlsdfnbch/Pysher) library.

A big thanks to @aaugustin for developing the [WebSockets](https://github.com/aaugustin/websockets) library.


Copyright
---------

MTI License - See LICENSE for details.

Changelog
---------
## Version 0.2
### Fix
 - Bug fix for disconnect, added missing await  
## Version 0.1
### New
 - First Working Version  
