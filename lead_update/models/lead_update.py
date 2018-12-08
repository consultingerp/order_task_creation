# -*- coding: utf-8 -*-
from openerp import fields, models, exceptions, api, _
import re
import html5lib
# sudo pip install html5lib
from bs4 import BeautifulSoup

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    def lead_update(self):
        if self._context and self._context.get('active_ids'):
            for lead in self._context.get('active_ids'):
                lead_rec = self.browse(lead)
                for message in lead_rec.message_ids:
                    if message.message_type == 'email':
                        body = message.body
                        import html2text
                        new_str = html2text.html2text(body)
                        convert = str(new_str)
                        d = html5lib.parseFragment(body)
                        s = ''.join(d.itertext())
                        lead_rec.description = (s)
                        message.unlink()
                        if lead_rec.description:
                            pdf_str = False
                            ldescription = lead_rec.description
                            desc = ldescription.encode('ascii','ignore')
                            partner_rec = self.env['res.partner']
                            state_rec = self.env['res.country.state']
                            country_rec = self.env['res.country.state']
                            company = re.search(r'<company-name>(.*)</company-name>', desc, re.DOTALL)
                            if company and company.group(1):
                                lead_rec.partner_name = company.group(1)
                            street1= re.search(r'<street1>(.*)</street1>', desc, re.DOTALL)
                            if street1 and street1.group(1):
                                lead_rec.street = street1.group(1)
                            street2 = re.search(r'<street2>(.*)</street2>', desc, re.DOTALL)
                            if street2 and street2.group(1):
                                lead_rec.street2 = street2.group(1)
                            zip = re.search(r'<zip>(.*)</zip>', desc, re.DOTALL)
                            if zip and zip.group(1):
                                lead_rec.zip = zip.group(1)
                            city = re.search(r'<city>(.*)</city>', desc, re.DOTALL)
                            if city and city.group(1):
                                lead_rec.city = city.group(1)
                            email = re.search(r'<email>(.*)</email>', desc, re.DOTALL)
                            if email and email.group(1):
                                lead_rec.email_from = email.group(1)
                            function = re.search(r'<function>(.*)</function>', desc, re.DOTALL)
                            if function and function.group(1):
                                lead_rec.function = function.group(1)
                            phone = re.search(r'<phone>(.*)</phone>', desc, re.DOTALL)
                            if phone and phone.group(1):
                                lead_rec.phone = phone.group(1)
                            mobile = re.search(r'<mobile>(.*)</mobile>', desc, re.DOTALL)
                            if mobile and mobile.group(1):
                                lead_rec.mobile = mobile.group(1)
                            contactname = re.search(r'<contact-name>(.*)</contact-name>', desc, re.DOTALL)
                            if contactname and contactname.group(1):
                                lead_rec.contact_name = contactname.group(1)
                            fax = re.search(r'<fax>(.*)</fax>', desc, re.DOTALL)
                            if fax and fax.group(1):
                                lead_rec.fax = fax.group(1)
                            customer = re.search(r'<customer-name>(.*)</customer-name>', desc, re.DOTALL)
                            if customer and customer.group(1):
                                 p_company = partner_rec.search([('name','=',company.group(1))],limit=1)
                                 if p_company:
                                     partner = partner_rec.search([('name','=',customer.group(1)),('parent_id','=',p_company.id)],limit=1)
                                 else:
                                     partner = partner_rec.search([('name', '=', customer.group(1))],limit=1)
                                 if partner:
                                     lead_rec.partner_id = partner.id
                            state = re.search(r'<state>(.*)</state>', desc, re.DOTALL)
                            if state and state.group(1):
                                state_id = state_rec.search([('name', '=', state.group(1))], limit=1)
                                if state_id:
                                    lead_rec.state_id = state_id.id
                            country = re.search(r'<country>(.*)</country>', desc, re.DOTALL)
                            if country and country.group(1):
                                country_id = state_rec.search([('name', '=', country.group(1))], limit=1)
                                if country_id:
                                    lead_rec.country_id = country_id.id
                            
                            pdf_link = re.search(r'<pdf_link>(.*)</pdf_link>', desc, re.DOTALL)
                            if pdf_link and pdf_link.group(1):
                                pdf_str = pdf_link.group(1)
                                
                            # Check for description field
                            # bod = re.search(r'&lt;body&gt;(.*)&lt;/body&gt;', convert, re.DOTALL)
                            bod = re.search(r'<body>(.*)</body>', desc, re.DOTALL)
                            if bod and bod.group(1):
                                lead_rec.description = bod.group(1)
                                if pdf_str:
                                    # description = lead_rec.description
                                    description = "\nPDF LINK: " + pdf_str
                                    lead_rec.description += description

