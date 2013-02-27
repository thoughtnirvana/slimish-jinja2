from flask import Flask
from flask import render_template
from slimish_jinja import SlimishExtension


class MyApp(Flask):
    jinja_options = Flask.jinja_options
    jinja_options['extensions'].append(SlimishExtension)

app = MyApp(__name__)
app.debug = True

@app.route('/')
def hello_slim():
    users = [{'name': 'first1', 'last_name': 'last1'},
             {'name': 'first2', 'middle_name': 'middle2'},
             {'name': 'first3'}]
    return render_template('demo.slim', users=users, content='content', user_class='user_class')

if __name__  == '__main__':
    app.run()
