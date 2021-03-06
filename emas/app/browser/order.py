from five import grok
from zope.interface import Interface
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName

from emas.theme.interfaces import IEmasServiceCost

grok.templatedir('templates')

class Order(grok.View):
    """ Order form.
    """
    
    grok.context(Interface)
    grok.require('zope2.View')

    def __call__(self):
        missing_input = False
        form_submitted = False
        self.subjects = self.request.get('subjects', None)

        if self.request.has_key('login.form.submitted'):
            membership_tool = getToolByName(self.context, 'portal_membership')
            membership_tool.loginUser(self.request)

        if self.request.has_key('order.form.submitted'):
            form_submitted = True
            if not self.subjects:
                missing_input = True

        elif self.request.has_key('mobileorder.form.submitted'):
            form_submitted = True

            # The mobile form submits the subject/grade as one compound value
            # place them on the request so everything else continues to work
            if 'item' in self.request:
                subjects, grade = self.request.get('item').split('-')
                self.request['subjects'] = subjects
                self.request['grade'] = 'grade' + grade

            required_fields = ['subjects', 'grade', 'service', 'prod_payment']
            pps = self.context.restrictedTraverse('@@plone_portal_state')
            for fieldname in required_fields:
                if self.request.get(fieldname, None) is None:
                    missing_input = True

            if missing_input:
                ptool = pps.portal().plone_utils
                ptool.addPortalMessage('All fields are required.',
                                        'warning')

        if form_submitted and not missing_input:
            # traverse to confirm if form has required fields
            view = self.context.restrictedTraverse('@@confirm')
            return view()
        else:
            return super(Order, self).__call__()

    def update(self):
        if (self.request.has_key('order.form.submitted') or
                self.request.has_key('mobileorder.form.submitted')):
            pmt = getToolByName(self.context, 'portal_membership')
            if pmt.isAnonymousUser():
                self.context.restrictedTraverse('logged_in')()

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IEmasServiceCost)
        self.practiceprice = settings.practiceprice
        self.textbookprice = settings.textbookprice
        self.textbook_and_practiceprice = (
            self.practiceprice + self.textbookprice)

    def products_and_services(self):
        pps = self.context.restrictedTraverse('@@plone_portal_state')
        products_and_services = pps.portal()._getOb('products_and_services')
        return products_and_services.getFolderContents(full_objects=True)

    def action(self, isAnon):
        """ Post to the current view in order to validate the form.
            We need enough info on the form for the confirm view to work.
        """
        return '%s/@@order' %self.context.absolute_url()
        
    def subject_selected(self, subject, selected):
        return subject == selected and 'checked' or ''

    def grade(self):
        return self.request.get('grade', '')

    def grade_selected(self, grade, selected):
        return grade == selected and 'checked' or ''

    def service(self):
        return self.request.get('service', '')

    def service_selected(self, service, selected):
        return service == selected and 'checked' or ''

    def prod_payment(self):
        return self.request.get('prod_payment', '')

    def prod_payment_selected(self, prod_payment, selected):
        return prod_payment == selected and 'checked' or ''

    def ordernumber(self):
        return self.request.get('ordernumber', '')

