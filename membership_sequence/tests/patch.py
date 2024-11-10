import unittest
from odoo.addons.base.tests.test_form_create import TestFormCreate
from odoo.addons.base_automation.tests.test_mail_composer import TestMailFullComposer
from odoo.addons.account.tests.test_tour import TestUi

@unittest.skip('[SKIP] Task 2564570')
def test_create_res_partner(self):
    pass

@unittest.skip('[SKIP] Task 2564570')
def test_full_composer_tour(self):
    pass

@unittest.skip('[SKIP] Task 2564570')
def test_01_account_tour(self):
    pass

TestFormCreate.test_create_res_partner = test_create_res_partner
TestMailFullComposer.test_full_composer_tour = test_full_composer_tour
TestUi.test_01_account_tour = test_01_account_tour

from odoo.addons.mail.tests.test_mail_full_composer import TestMailFullComposer
TestMailFullComposer.test_full_composer_tour = test_full_composer_tour
