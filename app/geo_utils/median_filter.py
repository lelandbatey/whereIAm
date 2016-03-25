# -*- coding: utf-8 -*-

"""Filtering of a collection by median."""

from __future__ import division, print_function


def get_candidates(data, index, winlen):
    """Given a collection (`data`) and an index (`index`) within that
    collection, return a collection of length `winlen` selected from `data`
    that is "centered around" `index`. `winlen` must be an odd integer.

    If a selection is requested at the beginning or end of the collection, and
    the window size is too large, the returned collection of candidates will
    have dummy data at the beginning/end that is a replication of the
    first/last item in the collection."""

    too_short = False
    too_long = False

    # `winlen` must be an odd integer
    assert (winlen % 2) == 1.0
    # Calculate a bounded start index, middle index, and end index
    middle = winlen // 2
    start = index-middle
    if start < 0:
        start = 0
        too_short = True
    end = index+middle
    if end > len(data)-1:
        end = len(data)-1
        too_long = True

    # Copy all the items from `start` to `end` into `candidates`
    calc_desired = end - start+1
    candidates = []
    while len(candidates) < calc_desired:
        candidates.append(data[start])
        start += 1

    # In cases where there's not enough data at the start or end, fill it in
    # with replicas of the start/end piece of data
    while len(candidates) < winlen:
        if too_short:
            candidates.insert(0, candidates[0])
        if too_long and len(candidates) < winlen:
            candidates.append(candidates[-1])

    assert len(candidates) == winlen
    return candidates


def median_filter(data, winlen=3):
    medians = []
    middle = winlen // 2

    for item in range(0, len(data)):
        candidates = sorted(get_candidates(data, item, winlen))
        medians.append(candidates[middle])
    return medians


