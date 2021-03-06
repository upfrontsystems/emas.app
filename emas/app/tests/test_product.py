import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.dexterity.interfaces import IDexterityFTI

from emas.app.product import IProduct
from emas.app.tests.base import INTEGRATION_TESTING


class TestProductIntegration(unittest.TestCase):
    """Unit test for the Product type
    """

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'testfolder')
        self.folder = self.portal.testfolder
    
    def test_adding(self):
        self.folder.invokeFactory('emas.app.product', 'product1')
        p1 = self.folder['product1']
        self.failUnless(IProduct.providedBy(p1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.product')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.product')
        schema = fti.lookupSchema()
        self.assertEquals(IProduct, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='emas.app.product')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IProduct.providedBy(new_object))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
