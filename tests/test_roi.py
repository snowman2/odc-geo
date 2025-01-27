import numpy as np
import pytest

from odc.geo.roi import (
    Tiles,
    _norm_slice_or_error,
    polygon_path,
    roi_boundary,
    roi_center,
    roi_from_points,
    roi_intersect,
    roi_is_empty,
    roi_is_full,
    roi_normalise,
    roi_pad,
    roi_shape,
    scaled_down_roi,
    scaled_down_shape,
    scaled_up_roi,
    w_,
)


def test_roi_tools():
    s_ = np.s_

    assert roi_shape(s_[2:4, 3:4]) == (2, 1)
    assert roi_shape(s_[:4, :7]) == (4, 7)
    assert roi_shape(s_[3, :7]) == (1, 7)

    assert roi_is_empty(s_[:4, :5]) is False
    assert roi_is_empty(s_[1:1, :10]) is True
    assert roi_is_empty(s_[7:3, :10]) is True

    assert roi_is_empty(s_[:3]) is False
    assert roi_is_empty(s_[4:4]) is True

    assert roi_is_full(s_[:3], 3) is True
    assert roi_is_full(s_[:3, 0:4], (3, 4)) is True
    assert roi_is_full(s_[:, 0:4], (33, 4)) is True
    assert roi_is_full(s_[1:3, 0:4], (3, 4)) is False
    assert roi_is_full(s_[1:3, 0:4], (2, 4)) is False
    assert roi_is_full(s_[0:4, 0:4], (3, 4)) is False
    assert roi_is_full(s_[0], 1) is True
    assert roi_is_full(s_[2], 3) is False

    roi = s_[0:8, 0:4]
    roi_ = scaled_down_roi(roi, 2)
    assert roi_shape(roi_) == (4, 2)
    assert scaled_down_roi(scaled_up_roi(roi, 3), 3) == roi

    assert scaled_down_shape(roi_shape(roi), 2) == roi_shape(scaled_down_roi(roi, 2))

    assert roi_shape(scaled_up_roi(roi, 10000, (40, 50))) == (40, 50)

    for bad_roi in [np.s_[1:], np.s_[:], np.s_[-3:]]:
        with pytest.raises(ValueError):
            _ = roi_shape(bad_roi)

    assert roi_normalise(s_[3:4], 40) == s_[3:4]
    assert roi_normalise(s_[3], 40) == s_[3:4]
    assert roi_normalise(s_[:4], (40,)) == s_[0:4]
    assert roi_normalise(s_[:], (40,)) == s_[0:40]
    assert roi_normalise(s_[:-1], (3,)) == s_[0:2]
    assert roi_normalise((s_[:-1],), 3) == (s_[0:2],)
    assert roi_normalise(s_[-2:-1, :], (10, 20)) == s_[8:9, 0:20]
    assert roi_normalise(s_[-2:-1, :, 3:4], (10, 20, 100)) == s_[8:9, 0:20, 3:4]
    assert roi_center(s_[0:3]) == 1.5
    assert roi_center(s_[0:2, 0:6]) == (1, 3)


def test_roi_from_points():
    roi = np.s_[0:2, 4:13]
    xy = roi_boundary(roi)

    assert xy.shape == (4, 2)
    assert roi_from_points(xy, (2, 13)) == roi

    xy = np.asarray(
        [
            [0.2, 1.9],
            [10.3, 21.2],
            [float("nan"), 11],
            [float("inf"), float("-inf")],
        ]
    )
    assert roi_from_points(xy, (100, 100)) == np.s_[1:22, 0:11]
    assert roi_from_points(xy, (5, 7)) == np.s_[1:5, 0:7]
    assert roi_from_points(xy[2:, :], (3, 3)) == np.s_[0:0, 0:0]


def test_roi_intersect():
    s_ = np.s_
    roi = s_[0:2, 4:13]

    assert roi_intersect(roi, roi) == roi
    assert roi_intersect(s_[0:3], s_[1:7]) == s_[1:3]
    assert roi_intersect(s_[0:3], (s_[1:7],)) == s_[1:3]
    assert roi_intersect((s_[0:3],), s_[1:7]) == (s_[1:3],)

    assert roi_intersect(s_[4:7, 5:6], s_[0:1, 7:8]) == s_[4:4, 6:6]


def test_roi_pad():
    s_ = np.s_
    assert roi_pad(s_[0:4], 1, 4) == s_[0:4]
    assert roi_pad(s_[0:4], 1, (4,)) == s_[0:4]
    assert roi_pad((s_[0:4],), 1, 4) == (s_[0:4],)

    assert roi_pad(s_[0:4, 1:5], 1, (4, 6)) == s_[0:4, 0:6]
    assert roi_pad(s_[2:3, 1:5], 10, (7, 9)) == s_[0:7, 0:9]
    assert roi_pad(s_[3, 0, :2], 1, (100, 100, 100)) == s_[2:5, 0:2, 0:3]


def test_norm_slice_or_error():
    s_ = np.s_
    assert _norm_slice_or_error(s_[0]) == s_[0:1]
    assert _norm_slice_or_error(s_[3]) == s_[3:4]
    assert _norm_slice_or_error(s_[:3]) == s_[0:3]
    assert _norm_slice_or_error(s_[10:100:3]) == s_[10:100:3]

    for bad in [np.s_[1:], np.s_[:-3], np.s_[-3:], np.s_[-2:10], -3]:
        with pytest.raises(ValueError):
            _ = _norm_slice_or_error(bad)


def test_window_from_slice():
    s_ = np.s_

    assert w_[None] is None
    assert w_[s_[:3, 4:5]] == ((0, 3), (4, 5))
    assert w_[s_[0:3, :5]] == ((0, 3), (0, 5))
    assert w_[list(s_[0:3, :5])] == ((0, 3), (0, 5))

    for roi in [s_[:3], s_[:3, :4, :5], 0]:
        with pytest.raises(ValueError):
            _ = w_[roi]


def test_polygon_path():
    pp = polygon_path([0, 1])
    assert pp.shape == (2, 5)
    assert set(pp.ravel()) == {0, 1}

    pp2 = polygon_path([0, 1], [0, 1])
    assert (pp2 == pp).all()

    pp = polygon_path([0, 1], [2, 3])
    assert set(pp[0].ravel()) == {0, 1}
    assert set(pp[1].ravel()) == {2, 3}


def test_tiles():
    tt = Tiles((10, 20), (3, 7))
    assert tt.tile_shape((0, 0)) == (3, 7)
    assert tt.shape.yx == (4, 3)
    assert tt.base.yx == (10, 20)

    assert tt[0, 0] == np.s_[0:3, 0:7]
    assert tt[3, 2] == np.s_[9:10, 14:20]
