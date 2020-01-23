# -*- coding: utf-8 -*-

import base64
import requests
import csv
import sys
import xml.etree.ElementTree as ElementTree
from odoo import api, fields, registry, models, _
from datetime import date, datetime
from odoo.tools import float_compare

from logging import getLogger
_logger = getLogger(__name__)

COUNTRIES = {
	'Sverige': 'Sweden',
	'Norge': 'Norway'
}

class AirflowImportWizard(models.Model):
	_name = 'airflow.import.wizard'
	_description = 'Airflow Import Wizard'

	path = fields.Char(string='Folder path', reqired=True)

	'''
		If 'Faktura' in firstname or lastname:
		partner.type = 'invoice'
		else 'contact'

		If firstname/lastname -> child partner -> partner.company_type = 'person'
		If Parent doesnt exist, create new partner as parent with same name. Insert data later (if comes up from file)

		If not firstname/lastname -> parent partner -> partner.company_type = 'company'
		Check if parent exists.
		If exists: Update data
		If not exists: Create partner.

		contid - 
		custid - ref
		name - name
		category -
		department -
		phone - phone
		phone2 - mobile
		fax
		fax2
		email - email
		www - website
		federalid
		accountno
		contgroup
		street - street
		region
		zipcode - zip
		city - city
		country - country_id (res.country)
		firstname - partner name if exists
		lastname - partner name if exists
		phonework
		cpersfax
		title
		cpersemail
		cellular
		cpersgroup
		cpersid
		dstreet
		dregion
		dzipcode
		dcity

	'''

	def get_partner_vals(self, data):
		res = {}
		Partner = self.env['res.partner']

		if data.get('custid', False):
			res['ref'] = data.get('custid')

		if data.get('name', False):
			res['name'] = data.get('name')

		phone = data.get('phone', False)
		if not phone:
			phone = data.get('phone2', False)
		if phone:
			res['phone'] = phone

		if data.get('cellular', False):
			res['mobile'] = data.get('cellular')

		email = data.get('cpersemail', False)
		if not email:
			email = data.get('email', False)
		if email:
			res['email'] = email

		if data.get('www', False):
			res['website'] = data.get('www')

		street = data.get('dstreet', False)
		if not street:
			street = data.get('street', False)
		if street:
			res['street'] = street

		zipcode = data.get('dzipcode', False)
		if not zipcode:
			zipcode = data.get('zipcode', False)
		if zipcode:
			res['zip'] = data.get('zipcode')

		city = data.get('dcity', False)
		if not city:
			city = data.get('city', False)
		if city:
			res['city'] = data.get('city')


		if data.get('country', False):
			country = self.env['res.country'].search([('name', '=', COUNTRIES[data.get('country')])])
			res['country_id'] = country.id

		if data.get('firstname', False) and data.get('lastname', False):
			res['name'] = data.get('firstname') + " " + data.get('lastname')
			res['company_type'] = 'person'
			if 'faktura' in data.get('firstname').lower() or 'faktura' in data.get('lastname').lower():
				res['type'] = 'invoice'
			else:
				res['type'] = 'contact'

			parent = Partner.search([('name', '=', data.get('name'))])
			if not parent:
				country = self.env['res.country'].search([('name', '=', COUNTRIES[data.get('country')])])
				if country:
					c_id = country.id
				else:
					c_id = False

				parent = Partner.create({
						'name': data.get('name'),
						'company_type': 'company',
						'ref': data.get('custid', False),
						'email': data.get('email', False),
						'phone': data.get('phone', False),
						'website': data.get('www', False),
						'street': data.get('street', False),
						'city': data.get('city', False),
						'zip': data.get('zipcode', False),
						'country_id': c_id
					})
			res['parent_id'] = parent.id

		elif data.get('firstname', False):
			res['name'] = data.get('firstname')
			res['company_type'] = 'person'
			if 'faktura' in data.get('firstname').lower():
				res['type'] = 'invoice'
			else:
				res['type'] = 'contact'

			parent = Partner.search([('name', '=', data.get('name'))])
			if not parent:
				country = self.env['res.country'].search([('name', '=', COUNTRIES[data.get('country')])])
				if country:
					c_id = country.id
				else:
					c_id = False
					
				parent = Partner.create({
						'name': data.get('name'),
						'company_type': 'company',
						'ref': data.get('custid', False),
						'email': data.get('email', False),
						'phone': data.get('phone', False),
						'website': data.get('www', False),
						'street': data.get('street', False),
						'city': data.get('city', False),
						'zip': data.get('zipcode', False),
						'country_id': c_id
					})
			res['parent_id'] = parent.id

		elif data.get('lastname', False):
			res['name'] = data.get('lastname')
			res['company_type'] = 'person'
			if 'faktura' in data.get('lastname').lower():
				res['type'] = 'invoice'
			else:
				res['type'] = 'contact'

			parent = Partner.search([('name', '=', data.get('name'))])
			if not parent:
				country = self.env['res.country'].search([('name', '=', COUNTRIES[data.get('country')])])
				if country:
					c_id = country.id
				else:
					c_id = False
					
				parent = Partner.create({
						'name': data.get('name'),
						'company_type': 'company',
						'ref': data.get('custid', False),
						'email': data.get('email', False),
						'phone': data.get('phone', False),
						'website': data.get('www', False),
						'street': data.get('street', False),
						'city': data.get('city', False),
						'zip': data.get('zipcode', False),
						'country_id': c_id
					})
			res['parent_id'] = parent.id
		else:
			res['type'] = 'contact'
			res['company_type'] = 'company'
			partner_exists = Partner.search([('name', '=', data.get('name')), ('ref', '=', data.get('custid'))])
			if partner_exists:
				res['write'] = partner_exists.id

		return res


	def import_partners(self):
		Partner = self.env['res.partner']
		i = 0

		with open(str(self.path) + '/contacts.csv', mode='r') as csv_file:
			csv_reader = csv.DictReader(csv_file, delimiter=";")
			for row in csv_reader:
				vals = self.get_partner_vals(row)
				if vals.get('write', False):
					company = Partner.browse(vals.get('write'))
					vals.pop('write', None)
					company.write(vals)
				else:
					Partner.create(vals)

				_logger.info(i)
				i += 1

	def get_order_line_vals(self, data):
		SaleOrderLine = self.env['sale.order.line']
		Product = self.env['product.product']
		res = {}

		prod_code = data.get('PROD_ID', False).strip()
		if not prod_code:
			note = data.get('PROD_NAME', False).strip()
			if note:
				res['note'] = note
			return res
		if prod_code:
			prod_code = prod_code.lstrip('0')
			product = Product.search([('default_code', '=', prod_code)])
			if product:
				res['product_id'] = product.id

				qty = data.get('QTY', False)
				if qty:
					qty = float(qty.strip())

				price = data.get('EX_Mva', False)
				if price:
					price = float(price.strip())

				discount = data.get('Discount', False)
				if discount:
					discount = float(discount.strip())

				res['product_uom_qty'] = qty
				res['price_unit'] = price
				res['discount'] = discount

		return res

	def get_sale_order_create_vals(self, data):
		SaleOrder = self.env['sale.order']
		Partner = self.env['res.partner']
		res = {}

		client_id = data.get('CLIENTID', False)
		if client_id:
			partner = Partner.search([('ref', '=', client_id), ('parent_id', '=', False)])
			res['partner_id'] = partner.id

		order_nr = data.get('ORDERNR', False)
		if order_nr:
			res['client_order_ref'] = order_nr

		web_order_nr = data.get('WEB_ORDER_NR', False)
		if web_order_nr:
			res['web_order_nr'] = web_order_nr.strip()

		order_date = data.get('Order_date', False)
		if order_date:
			res['date_order'] = datetime.strptime(order_date, '%m/%d/%Y')

		order_line = self.get_order_line_vals(data)
		note = order_line.get('note', False)
		if note:
			res['note'] = note
		if not note and order_line:
			res['order_line'] = [(0, 0, order_line)]

		res['state'] = 'done'

		return res

	def import_sale_orders(self):
		SaleOrder = self.env['sale.order']
		no_order_nr_list = []
		negative_qty_list = []
		partner_not_found_list = []
		i = 0

		filename = self._context.get('button_id')

		with open(str(self.path) + "/" + str(filename), mode='r') as csv_file:
			csv_reader = csv.DictReader(csv_file, delimiter=";")
			for row in csv_reader:
				if negative_qty_list:
					last_order_id = negative_qty_list[-1].get('ORDERNR', False)
				else:
					last_order_id = False

				order_nr = row.get('ORDERNR', False)
				if order_nr:
					if last_order_id:
						if order_nr == last_order_id:
							negative_qty_list.append(row)
							continue
					order_exists = SaleOrder.search([('client_order_ref', '=', order_nr)])
				if not order_nr:
					no_order_nr_list.append(row)
					continue

				qty = row.get('QTY', False)
				try:
					qty = float(qty)
				except ValueError:
					continue

				if float(qty) < 0:
					negative_qty_list.append(row)
					if order_exists:
						order_exists.action_cancel()
						order_exists.unlink()
						continue
					if not order_exists:
						continue

				if order_exists:
					update_vals = self.get_order_line_vals(row)
					note = update_vals.get('note', False)
					if note:
						current_note = order_exists.note
						new_note = str(current_note) + "\n" + note
						order_exists.write({
								'note': new_note
							})
					if not note and update_vals:
						order_exists.write({
								'order_line': [(0, 0, update_vals)]
							})
				else:
					create_vals = self.get_sale_order_create_vals(row)
					partner_id = create_vals.get('partner_id', False)
					if not partner_id:
						partner_not_found_list.append(row)
						continue
					order_exists = SaleOrder.create(create_vals)

				_logger.info(i)
				i += 1

		_logger.info(no_order_nr_list)
		_logger.info(negative_qty_list)
		_logger.info(partner_not_found_list)

	def get_template_vals(self, data):
		res = {}

		code = data.get('PROD_ID', False)
		if code:
			res['default_code'] = code.lstrip('0')

		name = data.get('PROD_NAME', False)
		if name:
			res['name'] = name
			if 'posten' in name.lower() or 'frakt' in name.lower():
				res['type'] = 'service'
			else:
				res['type'] = 'product'

		price = data.get('EX_Mva', False)
		if price:
			res['list_price'] = price

		res['sale_ok'] = True
		res['purchase_ok'] = True

		return res


	def import_products(self):
		ProductTmpl = self.env['product.template']
		i = 0

		with open(str(self.path) + '/orders.csv', mode='r') as csv_file:
			csv_reader = csv.DictReader(csv_file, delimiter=";")
			for row in csv_reader:
				code = row.get('PROD_ID',False)
				if code:
					code = code.lstrip('0')
					prod_tmpl = ProductTmpl.search([('default_code', '=', code)])
					if not prod_tmpl:
						product_tmpl_vals = self.get_template_vals(row)
						prod_tmpl = ProductTmpl.create(product_tmpl_vals)

				_logger.info(i)
				i += 1

	def fix_so_web_order_nr(self):
		orders = self.env['sale.order'].search([])
		i = 0

		for order in orders:
			if order.web_order_nr:
				order.web_order_nr = order.web_order_nr.lstrip("0")

			_logger.info(i)
			i += 1

	def fix_sale_order_partner_id(self):
		Partner = self.env['res.partner']
		SaleOrder = self.env['sale.order']
		not_found = []
		i = 0

		filename = self._context.get('button_id')
		
		with open(str(self.path) + "/" + str(filename), mode='r') as csv_file:
			csv_reader = csv.DictReader(csv_file, delimiter=";")
			for row in csv_reader:
				email = row.get('User_email(username)', False)
				order_id = row.get('order_id', False)
				if email and order_id:
					partner = Partner.search([('email', '=', email)])
					sale_order = SaleOrder.search([('web_order_nr', '=', order_id)])
					if not sale_order:
						not_found.append(order_id)
						i += 1
						continue
					if not partner:
						partner = Partner.create({
								'name': email,
								'type': 'contact',
								'company_type': 'person',
								'email': email
							})
					if len(partner) > 1:
						for p in partner:
							if p.company_type == 'company':
								partner = p

					sale_order.write({
							'partner_id': partner.id
						})

				_logger.info(i)
				i += 1

			_logger.info(not_found)