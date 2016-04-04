from __future__ import unicode_literals
import os
import tempfile
import unittest

from mkdocs import exceptions
from mkdocs.config import base, defaults


class ConfigBaseTests(unittest.TestCase):

    def test_unrecognised_keys(self):

        c = base.Config(schema=defaults.DEFAULT_SCHEMA)
        c.load_dict({
            'not_a_valid_config_option': "test"
        })

        failed, warnings = c.validate()

        self.assertEqual(warnings, [
            ('not_a_valid_config_option',
                'Unrecognised configuration name: not_a_valid_config_option')
        ])

    def test_missing_required(self):

        c = base.Config(schema=defaults.DEFAULT_SCHEMA)

        errors, warnings = c.validate()

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], 'site_name')
        self.assertEqual(str(errors[0][1]), 'Required configuration not provided.')

        self.assertEqual(len(warnings), 0)

    def test_load_from_file(self):
        """
        Users can explicitly set the config file using the '--config' option.
        Allows users to specify a config other than the default `mkdocs.yml`.
        """

        config_file = tempfile.NamedTemporaryFile('w', delete=False)
        try:
            config_file.write("site_name: MkDocs Test\n")
            config_file.flush()
            config_file.close()

            cfg = base.load_config(config_file=config_file.name)
            self.assertIsInstance(cfg, base.Config)
            self.assertEqual(cfg['site_name'], 'MkDocs Test')
        finally:
            os.remove(config_file.name)

    def test_load_from_missing_file(self):

        self.assertRaises(exceptions.ConfigurationError,
                          base.load_config, config_file='missing_file.yml')

    def test_load_from_open_file(self):
        """
        `load_config` can accept an open file descriptor.
        """
        
        config_file = tempfile.NamedTemporaryFile('r+', delete=False)
        try:
            config_file.write("site_name: MkDocs Test\n")
            config_file.flush()

            cfg = base.load_config(config_file=config_file)
            self.assertIsInstance(cfg, base.Config)
            self.assertEqual(cfg['site_name'], 'MkDocs Test')
            # load_config will always close the file
            self.assertTrue(config_file.closed)
        finally:
            os.remove(config_file.name)

    def test_load_from_closed_file(self):
        """
        The `serve` command with auto-reload may pass in a closed file descriptor.
        Ensure `load_config` reloads the closed file.
        """

        config_file = tempfile.NamedTemporaryFile('w', delete=False)
        try:
            config_file.write("site_name: MkDocs Test\n")
            config_file.flush()
            config_file.close()

            cfg = base.load_config(config_file=config_file)
            self.assertIsInstance(cfg, base.Config)
            self.assertEqual(cfg['site_name'], 'MkDocs Test')
        finally:
            os.remove(config_file.name)

    def test_load_from_deleted_file(self):
        """
        Deleting the config file could trigger a server reload.
        """

        config_file = tempfile.NamedTemporaryFile('w', delete=False)
        try:
            config_file.write("site_name: MkDocs Test\n")
            config_file.flush()
            config_file.close()
        finally:
            os.remove(config_file.name)
        self.assertRaises(exceptions.ConfigurationError,
                          base.load_config, config_file=config_file)

    def test_load_missing_required(self):
        """
        `site_name` is a required setting.
        """

        config_file = tempfile.NamedTemporaryFile('w', delete=False)
        try:
            config_file.write(
                "site_dir: output\nsite_uri: http://www.mkdocs.org\n")
            config_file.flush()
            config_file.close()

            self.assertRaises(exceptions.ConfigurationError,
                              base.load_config, config_file=config_file.name)
        finally:
            os.remove(config_file.name)
