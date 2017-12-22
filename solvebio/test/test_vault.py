from __future__ import absolute_import

from .helper import SolveBioTestCase


class VaultTests(SolveBioTestCase):

    def test_vaults(self):
        vaults = self.client.Vault.all()
        vault = vaults.data[0]
        self.assertTrue('id' in vault,
                        'Should be able to get id in vault')

        vault2 = self.client.Vault.retrieve(vault.id)
        self.assertEqual(vault, vault2,
                         "Retrieving vault id {0} found by all()"
                         .format(vault.id))

        check_fields = [
            'account_id', 'created_at', 'description', 'has_children',
            'has_folder_children', 'id', 'is_deleted', 'is_public',
            'last_synced', 'name', 'permissions', 'provider',
            'require_unique_paths', 'updated_at', 'url', 'user_id',
            'vault_properties', 'vault_type'
        ]

        for f in check_fields:
            self.assertTrue(f in vault, '{0} field is present'.format(f))

    def test_vault_paths(self):
        vaults = self.client.Vault.all()
        for vault in vaults:
            v, v_paths = self.client.Vault.validate_path(vault.full_path)
            self.assertEqual(v, vault.full_path)

        domain = self.client.User.retrieve().account.domain
        test_cases = [
            ['myVault', '{0}:myVault'.format(domain)],
            ['{0}:myVault'.format(domain), '{0}:myVault'.format(domain)],
            ['acme:myVault', 'acme:myVault'],
            # this assumes user f-ed and forgot the semi-colon for path
            ['acme:myVault/uploads_folder', 'acme:myVault'],
            ['myVault/uploads_folder', '{0}:myVault'.format(domain)],
        ]
        for case, expected in test_cases:
            v, v_paths = self.client.Vault.validate_path(case)
            self.assertEqual(v, expected)

        error_test_cases = [
            '',
            'myDomain:myVault:/the/heack',
            'oops:myDomain:myVault',
        ]
        for case in error_test_cases:
            with self.assertRaises(Exception):
                v, v_paths = self.client.Vault.validate_path(case)
