from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph import GlobbingFilter
from pycallgraph.output import GraphvizOutput

proxy_server = __import__('proxy-server')
import proxy_server 

config = Config()
config.trace_filter = GlobbingFilter(exclude=[
    'pickle.*',
    'threading.*',
    'StringIO.*',
    'inspect.*',
    'collections.*',
    'json.*'
    ])

graphviz = GraphvizOutput(output_file='filter_exclude.png')

