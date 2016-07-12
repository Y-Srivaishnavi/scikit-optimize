import numpy as np

from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_almost_equal
from sklearn.utils.testing import assert_array_equal
from sklearn.utils.testing import assert_less
from sklearn.utils.testing import assert_raise_message

from skopt.benchmarks import bench1
from skopt.benchmarks import bench2
from skopt.benchmarks import bench3
from skopt.benchmarks import branin
from skopt.benchmarks import hart6
from skopt.tree_opt import gbrt_minimize
from skopt.tree_opt import et_minimize
from skopt.tree_opt import rf_minimize
from skopt.tree_opt import tree_minimize


def check_no_iterations(minimizer):
    assert_raise_message(ValueError, "at least one iteration",
                         minimizer,
                         branin, [(-5.0, 10.0), (0.0, 15.0)], maxiter=0,
                         random_state=1)

    assert_raise_message(ValueError, "at least one starting point",
                         minimizer,
                         branin, [(-5.0, 10.0), (0.0, 15.0)], n_start=0,
                         maxiter=2, random_state=1)


def test_no_iterations():
    yield (check_no_iterations, gbrt_minimize)
    yield (check_no_iterations, et_minimize)
    yield (check_no_iterations, tree_minimize)
    yield (check_no_iterations, rf_minimize)


def test_one_iteration():
    result = gbrt_minimize(branin, [(-5.0, 10.0), (0.0, 15.0)],
                           maxiter=1, random_state=1)

    assert_equal(len(result.models), 0)
    assert_array_equal(result.x_iters.shape, (1, 2))
    assert_array_equal(result.func_vals.shape, (1,))
    assert_array_equal(result.x, result.x_iters[np.argmin(result.func_vals)])
    assert_almost_equal(result.fun, branin(result.x))


def test_seven_iterations():
    result = gbrt_minimize(branin, [(-5.0, 10.0), (0.0, 15.0)],
                           n_start=3, maxiter=7, random_state=1)

    assert_equal(len(result.models), 4)
    assert_array_equal(result.x_iters.shape, (7, 2))
    assert_array_equal(result.func_vals.shape, (7,))
    assert_array_equal(result.x, result.x_iters[np.argmin(result.func_vals)])
    assert_almost_equal(result.fun, branin(result.x))


def check_minimize(minimizer, func, y_opt, dimensions, margin, maxiter):
    r = minimizer(func, dimensions, maxiter=maxiter, random_state=1)
    assert_less(r.fun, y_opt + margin)


def test_tree_based_minimize():
    for minimizer in (tree_minimize, et_minimize, rf_minimize, gbrt_minimize):
        yield (check_minimize, minimizer, bench1, 0., [(-2.0, 2.0)], 0.05, 75)
        yield (check_minimize, minimizer, bench2, -5, [(-6.0, 6.0)], 0.05, 75)
        yield (check_minimize, minimizer, bench3, -0.9, [(-2.0, 2.0)], 0.05, 75)
        yield (check_minimize, minimizer, branin, 0.39,
               [(-5.0, 10.0), (0.0, 15.0)], 0.1, 100)
        yield (check_minimize, minimizer, hart6, -3.32,
               np.tile((0.0, 1.0), (6, 1)), 1.0, 200)
