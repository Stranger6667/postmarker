.. _templates:

Templates
=========

The Templates API is available via the ``templates`` manager:

.. code-block:: python

    >>> template = postmark.templates.get(983381)
    >>> template
    <Template: Test (983381)>
    >>> template.edit(Name='New name')
    >>> postmark.templates.all()
    [<Template: Test1 (983381)>, <Template: TestX (1003801)>]

To send an email based on the template, use send_with_template:

.. code-block:: python

    postmark.emails.send_with_template(
        TemplateId=123456,
        TemplateModel={
            "foo": "bar"
        },
        From="sender@example.com",
        To="johndoe@example.com",
    )

Template validation:

.. code-block:: python

    >>> postmark.templates.validate(Subject='Test', TextBody='Test')
    {
        'AllContentIsValid': True,
        'HtmlBody': None,
        'Subject': {
            'ContentIsValid': True,
            'RenderedContent': 'Test',
            'ValidationErrors': []
        },
        'SuggestedTemplateModel': {},
        'TextBody': {
            'ContentIsValid': True,
            'RenderedContent': 'Test',
            'ValidationErrors': []
        }
    }
