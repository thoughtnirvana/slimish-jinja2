from flask import Flask
from flask import render_template
from werkzeug import ImmutableDict
from slimish_jinja import SlimishExtension


class MyApp(Flask):
    jinja_options = Flask.jinja_options
    jinja_options['extensions'].append(SlimishExtension)

app = MyApp(__name__)
app.debug = True

@app.route('/')
def hello_slim():
    users = [{'name': 'foo', 'last_name': 'bar'},
             {'name': 'bar', 'middle_name': 'baz'},
             {'name': 'baz'}]
    return render_template('demo.slim', users=users)

if __name__  == '__main__':
    app.run()
