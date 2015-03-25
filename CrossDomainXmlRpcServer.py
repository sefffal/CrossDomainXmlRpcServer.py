#!/usr/bin/python

"""
This is a subclass of the python standard module SimpleXMLRPCServer.
CrossDomainXmlRpcServer is designed to provide an ever so slightly simpler interface and allow for cross
domain XmlRpc requests from AJAX equiped web browsers using the new Access-Control-Allow-Origin headers (search for CORS).

The bulk of these features are implemented in CrossDomainXmlRpcRequestHandler (a subclass of SimpleXMLRPCRequestHandler).
"""


__author__ = "William Thompson"
__date__   = "16th March 2012"

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

# Note it has to sub class from object because SimpleXMLRPCServer is an old-style class and we want to use super()
class CrossDomainXmlRpcServer(SimpleXMLRPCServer, object):
    """
    """

    def __init__(self, port, allow_none=True, **kwargs):
        super(CrossDomainXmlRpcServer, self).__init__(("", port), requestHandler=CrossDomainXmlRpcRequestHandler, allow_none=allow_none, **kwargs)

class CrossDomainXmlRpcRequestHandler(SimpleXMLRPCRequestHandler):
    """
    This is an implementation of SimpleXMLRPCServer.SimpleXMLRPCRequestHandler that allows for javascript cross-origin access.
    It does this by sending the header "Access-Control-Allow-Origin: *"
    """
    
    rpc_paths = ('/rpc')
    
                
    # Written by Will to allow for CORS from javascript in browsers with access controls
    # When browsers wish to fetch something from another origin, they "preflight" it first. These headers respond to the
    # preflight saying that it's ok to fetch this from this server (even though we may be a differnt host).
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", self.headers.get("Access-Control-Request-Headers", "")) # Respond that they can send whatever headers they request to send
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS") 
        self.send_header("Access-Control-Max-Age", str(60*60*24*7)) # Cache answer for up to seven days
        self.send_header("Content-Length", "0") # Response body must be empty
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        

	# More or less ripped from SimpleXMLRPCServer
    def do_POST(self):
        """Handles the HTTP POST request.

        Attempts to interpret all HTTP POST requests as XML-RPC calls,
        which are forwarded to the server's _dispatch method for handling.
        """

        # Check that the path is legal
        if not self.is_rpc_path_valid():
            self.report_404()
            return

        try:
            # Get arguments by reading body of request.
            # We read this in chunks to avoid straining
            # socket.read(); around the 10 or 15Mb mark, some platforms
            # begin to have problems (bug #792570).
            max_chunk_size = 10*1024*1024
            size_remaining = int(self.headers["content-length"])
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                L.append(self.rfile.read(chunk_size))
                size_remaining -= len(L[-1])
            data = ''.join(L)

            data = self.decode_request_content(data)
            if data is None:
                return #response has been sent

            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch(
                    data, getattr(self, '_dispatch', None), self.path
                )
        except Exception, e: # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            self.send_response(500)

            # Send information about the exception if requested
            if hasattr(self.server, '_send_traceback_header') and \
                    self.server._send_traceback_header:
                self.send_header("X-exception", str(e))
                self.send_header("X-traceback", traceback.format_exc())

            self.send_header("Content-length", "0")
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            if self.encode_threshold is not None:
                if len(response) > self.encode_threshold:
                    q = self.accept_encodings().get("gzip", 0)
                    if q:
                        try:
                            response = xmlrpclib.gzip_encode(response)
                            self.send_header("Content-Encoding", "gzip")
                        except NotImplementedError:
                            pass
            self.send_header("Content-length", str(len(response)))
			
			# By Will:
			# This allows for javascript to make requests from the browser
            self.send_header("Access-Control-Allow-Origin", "*")
			
            self.end_headers()
            self.wfile.write(response)
