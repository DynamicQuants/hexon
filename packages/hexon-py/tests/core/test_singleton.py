from hexon.core.singleton import Singleton


@Singleton
class JustOne:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

    def decrement(self):
        self.value -= 1

    def get_value(self):
        return self.value


def test_singleton_state():
    just_one = JustOne()
    just_one.increment()
    assert just_one.get_value() == 1

    just_one = JustOne()
    just_one.increment()
    assert just_one.get_value() == 2

    just_one = JustOne()
    just_one.decrement()
    assert just_one.get_value() == 1

    just_one = JustOne()
    just_one.decrement()
    assert just_one.get_value() == 0


def test_singleton_instance():
    i1 = JustOne()
    i2 = JustOne()

    assert i1 is i2
    assert i1 == i2
    assert i1.get_value() == 0
    assert i2.get_value() == 0

    i1.increment()
    assert i1.get_value() == 1
    assert i2.get_value() == 1
