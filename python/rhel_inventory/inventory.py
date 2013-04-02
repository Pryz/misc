#!/usr/bin/python
'''
Author: Pryz
Date: oct. 15, 2012 
'''
import report
import os
import simplejson as json
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from jinja2 import Environment, FileSystemLoader

# Utils
def is_valid_url(url):
    parts = urlparse.urlparse(url)
    return parts.scheme in ('http', 'https')

def get_hostname(url):
    return urlparse.urlparse(url).netloc

# Inventory class
class Inventory(object):

    def __init__(self):
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                     autoescape=True)
        self.jinja_env.filters['hostname'] = get_hostname
        
        self.url_map = Map([
          Rule('/', endpoint='index'),
          Rule('/refresh', endpoint='generate_report'),
        ])
  
    def on_index(self, request):
        error = None
        url = ''
        # Read .json vm list
        f = open(os.path.join(os.path.dirname(__file__), 'data/vm_list_infos.json'))
        data_json = f.read()
        f.close()
        data = json.loads(data_json) 
        # Example 3 - Read File with Exception Handling
        # Display page
        return self.render_template('index.html', error=error, url=url, data=data, nb_vm=len(data))
    
    def on_generate_report(self, request):
        error = None
        url = ''
        hyp_config = {'user': 'user', 'password': 'password', 'vcenter': 'vcenter'} 
        report = Report(hyp_config)
        try:
            server = report.connect()
        except Error:
            return Response("error", status=500)
  
        report.report_to_file(report.generate_report(server))
        report.disconnect()
  
        return Response("ok", status=200)
  
    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype='text/html')
    
    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except NotFound, e:
            return self.error_404()
        except HTTPException, e:
            return e
    
    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)
    
    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
  
    def error_404(self):
        response = self.render_template('404.html')
        response.status_code = 404
        return response


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = Inventory()
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/static': os.path.join(os.path.dirname(__file__), 'static')
    })
    run_simple('0.0.0.0', 5000, app, use_debugger=True, use_reloader=True)



