long_doc = """
## [Slim](http://slim-lang.com/) templates syntax for Jinja2.


#### Installation

I will be uploading it to PyPi soon. By then, clone the repository. Examples of using it as `Jinja2
extension(jinja_demo.py)`,
with `Flask(flask_demo.py)` and standalone`(convert.py and demo.py)` are bundled.

If you want to use it for any other purpose, the `lexer - lexer.py` and `parser - parser.py` are simple enough.
`lexer` reads the input by lines and generates tokens. `parser` implements a hand rolled recursive descent parser.

For quick reference, this slim::

    !5
    html
      head
        / Inline static content.
        title
        -block title
           |Slimish-Jinja Example
        / Self closing tag with attributes.
        meta name="keywords" content="template language"
        script
          / Empty jinja tag.
          @block script

      / 'id' and 'class' shortcut.
      body#home.fluid.liquid
        / Nested static content.
        h1
          |This is my header.
        / 'div' with 'id' and 'class' shortcut.
        #contents.main
          / Empty html tag.
          %div
          p Dynamic =content
          p
            |Nested dyanmic =content
                    Left indent is preserved in text blocks.
          / Mixing html is fine as well.
          p
            |<a href\="http://www.thoughtnirvana.com">ThoughtNirvana</a>
          / Dynamic attributes.
          ul class="=user_class"
            / Jinja tag.
            -for user in users
              li =user.name
              -if user.last_name
                li =user.last_name
              -elif user.middle_name
                li =user.middle_name
            -else
              li No user found.


converts to::

    <!doctype html>
    <html>
    <head>
        <title>
        {% block title %}
            Slimish-Jinja Example
        {% endblock %}
        </title>
        <meta  content="template language" name="keywords"/>
        <script>
        {% block script %}{% endblock %}
        </script>
    </head>
    <body id="home" class="fluid liquid">
        <h1>
        This is my header.
        </h1>
        <div id="contents" class="main">
        <div></div>
        <p>Dynamic {{ content }}</p>
        <p>
            Nested dyanmic {{ content }}        Left indent is preserved in text blocks.
        </p>
        <p>
            <a href="http://www.thoughtnirvana.com">ThoughtNirvana</a>
        </p>
        </div>
        <ul  class="{{ user_class }}">
        {% for user in users %}
            <li>{{ user.name }}</li>
            {% if user.last_name %}
            <li>{{ user.last_name }}</li>
            {% elif user.middle_name %}
            <li>{{ user.middle_name }}</li>
            {% endif %}
        {% else %}
            <li>No user found.</li>
        {% endfor %}
        </ul>
    </body>
    </html>


#### Doctype delcarations.


    !html
    <!DOCTYPE html>

    !5
    <!DOCTYPE html>

    !1.1
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

    !strict
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

    !frameset
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">

    !mobile
    <!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.2//EN" "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile12.dtd">

    !basic
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN" "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd">

    !transitional
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">


    !strict
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">

    !frameset
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">

    !transitional
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">


#### Static content

    / Inline static content.
    h1 This is my header

    / Nested static content.
    h1
      |This is my header

    / Multiline static content.
    p
      |Span mutliple lines.
         Left indent preserved in the output.


#### Dynamic content

    / Inline
    h1 =user.title

    / Nested
    h1
      =user.title

    / Mixed with text.
    h1
      |The user name is =user.name


#### Jinja tags

    -for user in users
      li user.name
      -if user.lastname
        li user.lastname
    -else
      li No users found


#### Dynamic contents in attribute

      a href=user.url =user.name


#### **id** and **classname** shortcuts

    #contents.main.liquid => <div id="contents" class="main liquid">

    body#home.left => <body id="home" class="left">


#### Code comments.

    / Single slash comments.
    / Not part of the output.
    p This is content.


#### Empty html tags

    %div => <div></div>


#### Empty jinja tags.

    @block title => {%block title %}{% endblock %}

"""

from setuptools import setup
setup(name='slimish_jinja',
      version='0.1',
      packages=['slimish_jinja'],
      scripts=['slim_to_jinja.py'],
      isntall_requires=['distribute', 'jinja2'],
      license='BSD',
      description='Slim templates syntax for Jinja2 templates',
      long_description=long_doc,
      author='Rahul Kumar',
      url='https://github.com/thoughtnirvana/slimish_jinja',
      author_email='rahul@thoughtnirvana.com',
     )
