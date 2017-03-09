"""Config file for webapp."""

from __future__ import print_function
import os, sys
import multiprocessing
import yaml
import glob


class warn_defaultdict(dict):
    """
    A recursive `collections.defaultdict`, but with printed warnings when
    an item is not found.

    >>> d = warn_defaultdict({1: 2})
    >>> d[2][3][4]
    [config] WARNING: non-existent key "2" requested
    [config] WARNING: non-existent key "3" requested
    [config] WARNING: non-existent key "4" requested

    >>> d = warn_defaultdict({'sub': {'a': 'b'}})
    >>> print(d['sub']['foo'])
    [config] WARNING: non-existent key "foo" requested
    {}

    """
    def update(self, other):
        for k, v in other.items():
            self.__setitem__(k, v)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = warn_defaultdict(value)

        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        if not key in self.keys():
            print('[config] WARNING: non-existent '
                  'key "{}" requested'.format(key))

            self.__setitem__(key, warn_defaultdict())

        return dict.__getitem__(self, key)



# Load configuration
config_files = glob.glob(
        os.path.join(os.path.dirname(__file__), '../config*.yaml')
        )

config_files = [os.path.abspath(cf) for cf in config_files]


# Load example config file as default template
cfg = warn_defaultdict()
cfg.update(yaml.load(open(os.path.join(os.path.dirname(__file__),
                                       "../config.yaml.example"))))

for cf in config_files:
    try:
        more_cfg = yaml.load(open(cf))
        print('[baselayer] Loaded {}'.format(cf))
        cfg.update(more_cfg)
    except IOError:
        pass

# Expand home variable;
cfg['paths'] = {key: os.path.expanduser(value)
                   for (key, value) in cfg['paths'].items()}
cfg['paths'] = {key: value.format(**cfg['paths'])
                   for (key, value) in cfg['paths'].items()}


del yaml, os, sys, print_function, config_files, multiprocessing

cfg['webapp'] = locals()


def show_config():
    """Print config settings to stdout (run on app start)."""
    print()
    print("=" * 78)
    print("baselayer configuration")

    for key in sorted(cfg):
        if key in cfg:
            print("-" * 78)
            print(key)

            if isinstance(cfg[key], dict):
                for key, val in cfg[key].items():
                    print('  ', key.ljust(30), val)

    print("=" * 78)

show_config()

