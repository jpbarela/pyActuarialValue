from io import StringIO

from lazyproperty.lazyproperty import lazyproperty


class TestLazy(object):

    def __init__(self, output):
        self.output = output

    @lazyproperty
    def expensive_property(self):
        self.output.write("some long calculation")
        return "my result"


def test_lazyproperty():
    out = StringIO()
    test_object = TestLazy(out)

    test_object.expensive_property
    output_first = out.getvalue().strip()
    assert output_first == 'some long calculation', \
        "Expected 'some long calculation' got {0}".format(output_first)

    test_object.expensive_property
    output_next = out.getvalue().strip()
    assert output_next == 'some long calculation', \
        "Expected 'some long calculation' got {0}".format(output_next)
