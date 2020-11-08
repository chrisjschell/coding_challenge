"""Input data for combine function"""

bitbucket = {
    'followers': 1,
    'languages': {'python'},
    'repos': {'forked': 1, 'unforked': 1},
    'watchers': 1
}

github = {
    'followers': 1,
    'languages': {'javascript'},
    'repos': {'forked': 1, 'unforked': 1},
    'topics': {'flask'},
    'watchers': 1
}

bitbucket_empty = {
    'followers': 0,
    'languages': set(),
    'repos': {'forked': 0, 'unforked': 0},
    'watchers': 0
}

github_empty = {
    'followers': 0,
    'languages': set(),
    'repos': {'forked': 0, 'unforked': 0},
    'topics': set(),
    'watchers': 0
}
