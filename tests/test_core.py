"""Tests for Guru."""
from src.core import Guru
def test_init(): assert Guru().get_stats()["ops"] == 0
def test_op(): c = Guru(); c.generate(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Guru(); [c.generate() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Guru(); c.generate(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Guru(); r = c.generate(); assert r["service"] == "guru"
