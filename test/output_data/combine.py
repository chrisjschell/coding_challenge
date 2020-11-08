"""Expected output data for combine function"""

expected_result = {
    'languages': {
        'list': [
            'javascript',
            'python'
        ],
        'count': 2
    },
    'topics': {
        'list': [
            'flask'
        ],
        'count': 1
    },
    'repos': {
        'forked': 2,
        'unforked': 2,
        'count': 4
    },
    'followers': 2,
    'watchers': 2
}

expected_empty = {
    'languages': {
        'list': [],
        'count': 0
    },
    'topics': {
        'list': [],
        'count': 0
    },
    'repos': {
        'forked': 0,
        'unforked': 0,
        'count': 0
    },
    'followers': 0,
    'watchers': 0
}
