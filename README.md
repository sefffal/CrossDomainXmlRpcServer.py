# CrossDomainXmlRpcServer.py

A subclass of the python 2 standard module SimpleXMLRPCServer with an ever so slightly simpler interface, and more importantly allow for cross-domain XmlRpc requests from AJAX equiped web browsers using the new Access-Control-Allow-Origin headers (search for CORS).

Specificaly, it works well with my [xml-rpc.js library](https://github.com/sefffal/xml-rpc.js "xml-rpc.js on GitHub")

The bulk of these features are implemented in CrossDomainXmlRpcRequestHandler (a subclass of SimpleXMLRPCRequestHandler).


## Examples

### Define python functions as usual

```python
# Return a number
def simple(a,b):
	return a+b

# Return something more complex
def complex(a, b):
	return [[i, i**2] for i in range(a,b)]

```

### Now create an XML-RPC server instance

```python
server = CrossDomainXmlRpcServer(addr, allow_none=True) # Allow None as a return value
# Register functions we created
server.register_function(simple)
server.register_function(complex)
# Can also register introspection functions (necessary for seamless interop with xml-rpx.js)
server.register_introspection_functions() # XmlRdp functions like list_methods, etc.

# Now begin serving
server.serve_forever()
```

### Register all the methods from an object

```python
# Define a class, or use any existing object
class ABC:
	def simple(self, a, b):
		return a+b

	def other(self, a, b, c):
		return self.simple(a,b)*c
# Create an isntance
myobj = ABC()

# Register instance, and begin serving
server = CrossDomainXmlRpcServer(addr, allow_none=True) # Allow None as a return value
server.register_instance(myobj)
server.register_introspection_function() # necessary for seamless interop with xml-rpx.js
server.serve_forever()
```

### Using ABC example class with xml-rpc.js

```javascript
var abc = new XmlRpcConnection({
    url:     "http://<server_url>",   // URL to XML-RPC service
});

abc.simple(1,3); // returns 4
abc.other(1,3,5); // returns 20
```