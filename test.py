from unittest import TestCase, main
from vm import execute
from io import StringIO


class TestExecute(TestCase):
    def test_output(self):
        buffer = StringIO()
        execute(".", output=buffer)
        self.assertEqual(buffer.getvalue(), chr(0))

    def test_input(self):
        input = StringIO("A")
        output = StringIO()
        execute(",.", input=input, output=output)
        self.assertEqual(input.getvalue(), "A")

    def test_move_right(self):
        buffer = StringIO()
        execute(">.", output=buffer)
        self.assertEqual(buffer.getvalue(), chr(0))

    def test_move_left(self):
        buffer = StringIO()
        execute("+><.", output=buffer)
        self.assertEqual(buffer.getvalue(), chr(1))

    def test_increment(self):
        buffer = StringIO()
        execute("+.", output=buffer)
        self.assertEqual(buffer.getvalue(), chr(1))

    def test_decrement(self):
        buffer = StringIO()
        execute("+-.", output=buffer)
        self.assertEqual(buffer.getvalue(), chr(0))

    def test_loop(self):
        buffer = StringIO()
        execute("++[>+<-]>.", output=buffer)
        self.assertEqual(buffer.getvalue(), chr(2))

    def test_full(self):
        buffer = StringIO()
        execute("++++++ [ > ++++++++++ < - ] > +++++ .", output=buffer)
        self.assertEqual(buffer.getvalue(), "A")


if __name__ == "__main__":
    main()
