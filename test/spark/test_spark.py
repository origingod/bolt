from numpy import arange
import pytest
from bolt import array
from bolt.spark.spark import BoltArraySpark
from bolt.utils import allclose

import generic

def test_construct(sc):

    x = arange(2*3*4).reshape((2, 3, 4))
    b = BoltArraySpark.fromarray(x, sc)
    assert isinstance(b, BoltArraySpark)
    assert allclose(b.toarray(), x)

    b = BoltArraySpark.fromarray(x, sc, split=2)
    assert isinstance(b, BoltArraySpark)
    assert allclose(b.toarray(), x)

    b = BoltArraySpark.fromarray(x, sc, split=3)
    assert isinstance(b, BoltArraySpark)
    assert allclose(b.toarray(), x)

    with pytest.raises(ValueError):
        BoltArraySpark.fromarray(x, sc, split=0)

    with pytest.raises(ValueError):
        BoltArraySpark.fromarray(x, sc, split=4)


def test_shape(sc):

    x = arange(2*3).reshape((2, 3))
    b = array(x, sc)
    assert b.shape == x.shape

    x = arange(2*3*4).reshape((2, 3, 4))
    b = array(x, sc)
    assert b.shape == x.shape


def test_size(sc):

    x = arange(2*3*4).reshape((2, 3, 4))
    b = array(x, sc, split=1)
    assert b.size == x.size


def test_split(sc):

    x = arange(2*3*4).reshape((2, 3, 4))
    b = array(x, sc, split=1)
    assert b.split == 1

    b = array(x, sc, split=2)
    assert b.split == 2


def test_mask(sc):

    x = arange(2*3*4).reshape((2, 3, 4))
    b = array(x, sc, split=1)
    assert b.mask == (1, 0, 0)

    b = array(x, sc, split=2)
    assert b.mask == (1, 1, 0)

    b = array(x, sc, split=3)
    assert b.mask == (1, 1, 1)


def test_value_shape(sc):

    x = arange(2*3).reshape((2, 3))
    b = array(x, sc)
    assert b.values.shape == (3,)

    x = arange(2*3*4).reshape((2, 3, 4))
    b = array(x, sc, split=1)
    assert b.values.shape == (3, 4)


def test_key_shape(sc):

    x = arange(2*3).reshape((2, 3))
    b = array(x, sc)
    assert b.keys.shape == (2,)

    x = arange(2*3*4).reshape((2, 3, 4))
    b = array(x, sc, split=2)
    assert b.keys.shape == (2, 3)


def test_reshape_keys(sc):

    x = arange(2*3*4).reshape((2, 3, 4))

    b = array(x, sc, split=2)
    c = b.keys.reshape((3, 2))
    assert c.keys.shape == (3, 2)
    assert allclose(c.toarray(), x.reshape((3, 2, 4)))

    b = array(x, sc, split=1)
    c = b.keys.reshape((2, 1))
    assert allclose(c.toarray(), x.reshape((2, 1, 3, 4)))

    b = array(x, sc, split=1)
    c = b.keys.reshape((2,))
    assert allclose(c.toarray(), x)

    b = array(x, sc, split=2)
    c = b.keys.reshape((2, 3))
    assert allclose(c.toarray(), x)

    b = array(x, sc, split=2)
    with pytest.raises(ValueError):
        b.keys.reshape((2, 3, 4))


def test_reshape_values(sc):

    x = arange(2*3*4).reshape((2, 3, 4))

    b = array(x, sc, split=1)
    c = b.values.reshape((4, 3))
    assert c.values.shape == (4, 3)
    assert allclose(c.toarray(), x.reshape((2, 4, 3)))

    b = array(x, sc, split=2)
    c = b.values.reshape((1, 4))
    assert allclose(c.toarray(), x.reshape((2, 3, 1, 4)))

    b = array(x, sc, split=2)
    c = b.values.reshape((4,))
    assert allclose(c.toarray(), x)

    b = array(x, sc, split=1)
    c = b.values.reshape((3, 4))
    assert allclose(c.toarray(), x)

    b = array(x, sc, split=2)
    with pytest.raises(ValueError):
        b.values.reshape((2, 3, 4))


def test_transpose_keys(sc):

    x = arange(2*3*4).reshape((2, 3, 4))

    b = array(x, sc, split=2)
    c = b.keys.transpose((1, 0))
    assert c.keys.shape == (3, 2)
    assert allclose(c.toarray(), x.transpose((1, 0, 2)))

    b = array(x, sc, split=1)
    c = b.keys.transpose((0,))
    assert allclose(c.toarray(), x)

    b = array(x, sc, split=2)
    c = b.keys.transpose((0, 1))
    assert allclose(c.toarray(), x)

    b = array(x, sc, split=2)
    with pytest.raises(ValueError):
        b.keys.transpose((0, 2))

    with pytest.raises(ValueError):
        b.keys.transpose((1, 1))

    with pytest.raises(ValueError):
        b.keys.transpose((0,))


def test_transpose_values(sc):

    x = arange(2*3*4).reshape((2, 3, 4))

    b = array(x, sc, split=1)
    c = b.values.transpose((1, 0))
    assert c.values.shape == (4, 3)
    assert allclose(c.toarray(), x.transpose((0, 2, 1)))

    b = array(x, sc, split=1)
    c = b.values.transpose((0, 1))
    assert allclose(c.toarray(), x)

    b = array(x, sc, split=2)
    c = b.values.transpose((0,))
    assert allclose(c.toarray(), x.reshape((2, 3, 4)))

    b = array(x, sc, split=1)
    with pytest.raises(ValueError):
        b.values.transpose((0, 2))

    with pytest.raises(ValueError):
        b.values.transpose((1, 1))

    with pytest.raises(ValueError):
        b.values.transpose((0,))


"""
Testing functional operators
"""

def test_map(sc):

    import random
    random.seed(42)

    x = arange(2*3*4).reshape(2, 3, 4)
    b = barray(x, sc, split=1)

    # Test all map functionality when the base array is split after the first axis
    generic.map_suite(x, b)

    # Split the BoltArraySpark after the second axis and rerun the tests
    b = barray(x, sc, split=1)
    generic.map_suite(x, b)

def test_reduce(sc):

    from numpy import asarray

    dims = (10, 10, 10)
    area = dims[0] * dims[1]
    arr = asarray([repeat(x,area).reshape(dims[0], dims[1]) for x in range(dims[2])])
    b = barray(arr, sc, split=1)

    # Test all reduce functionality when the base array is split after the first axis
    generic.reduce_suite(arr, b)

    # Split the BoltArraySpark after the second axis and rerun the tests
    b = barray(arr, sc, split=2)
    generic.reduce_suite(arr, b)


def test_filter(sc):

    x = arange(2*3*4).reshape(2, 3, 4)
    b = barray(x, sc, split=1)

    # Test all filter functionality when the base array is split after the first axis
    generic.filter_suite(x, b)

    # Split the BoltArraySpark after the second axis and rerun the tests
    b = barray(x, sc, split=1)
    generic.filter_suite(x, b)


def test_getitem_slice(sc):

    x = arange(2*3).reshape((2, 3))

    b = barray(x, sc, split=1)
    assert allclose(b[0:1, 0:1].toarray(), x[0:1, 0:1])
    assert allclose(b[0:2, 0:2].toarray(), x[0:2, 0:2])
    assert allclose(b[0:2, 0:3].toarray(), x[0:2, 0:3])
    assert allclose(b[0:2, 0:3:2].toarray(), x[0:2, 0:3:2])
    assert allclose(b[:2, :2].toarray(), x[:2, :2])
    assert allclose(b[1:, 1:].toarray(), x[1:, 1:])

    b = barray(x, sc, split=2)
    assert allclose(b[0:1, 0:1].toarray(), x[0:1, 0:1])
    assert allclose(b[0:2, 0:2].toarray(), x[0:2, 0:2])
    assert allclose(b[0:2, 0:3].toarray(), x[0:2, 0:3])
    assert allclose(b[0:2, 0:3:2].toarray(), x[0:2, 0:3:2])
    assert allclose(b[:2, :2].toarray(), x[:2, :2])
    assert allclose(b[1:, 1:].toarray(), x[1:, 1:])

def test_getitem_int(sc):

    x = arange(2*3).reshape((2, 3))

    b = barray(x, sc, split=1)
    assert allclose(b[0, 0].toarray(), x[0, 0])
    assert allclose(b[0, 1].toarray(), x[0, 1])
    assert allclose(b[0, 0:1].toarray(), x[0, 0:1])
    assert allclose(b[1, 2].toarray(), x[1, 2])

    b = barray(x, sc, split=2)
    assert allclose(b[0, 0].toarray(), x[0, 0])
    assert allclose(b[0, 1].toarray(), x[0, 1])
    assert allclose(b[0, 0:1].toarray(), x[0, 0:1])
    assert allclose(b[1, 2].toarray(), x[1, 2])
