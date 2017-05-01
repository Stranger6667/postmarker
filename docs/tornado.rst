.. _tornado:

Tornado helper
==============

There is a mixin for `Tornado <http://www.tornadoweb.org/>` support. You could implement request handler like this:

.. code-block:: python

    from postmarker.tornado import PostmarkMixin
    from tornado.web import RequestHandler


    class EmailHandler(PostmarkMixin, RequestHandler):

        def post(self):
            # Awesome stuff here
            # ...
            # Send single email
            self.send(
                From='sender@example.com',
                To='receiver@example.com',
                Subject='Postmark test',
                HtmlBody='<html><body><strong>Hello</strong> dear Postmark user.</body></html>'
            )
            # Send batch
            self.send_batch(
                {
                    'From': 'sender@example.com',
                    'To': 'receiver@example.com',
                    'Subject': 'Postmark test',
                    'HtmlBody': '<html><body><strong>Hello</strong> dear Postmark user.</body></html>',
                },
                {
                    'From': 'sender2@example.com',
                    'To': 'receiver2@example.com',
                    'Subject': 'Postmark test 2',
                    'HtmlBody': '<html><body><strong>Hello</strong> dear Postmark user.</body></html>',
                }
            )
            # Or do whatever you want to do with postmark
            bounces = self.postmark_client.bounces.all()

To make it work, define ``postmark_server_token`` option:


.. code-block:: python

    from tornado.web import Application

    app = Application(
        [
            (r'/send/', EmailHandler),
        ],
        postmark_server_token='YOUR_API_TOKEN'
    )

And run your app! That's it.
