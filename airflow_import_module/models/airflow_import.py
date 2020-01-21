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
			partner_exists = Partner.search([('name', '=', data.get('name'))])
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

	def get_sale_order_update_vals(self, data):
		return

	def get_sale_order_create_vals(self, data):
		return

	def import_sale_orders(self):
		SaleOrder = self.env['sale.order']
		i = 0

		with open(str(self.path) + '/orders.csv', mode='r') as csv_file:
			csv_reader = csv.DictReader(csv_file, delimiter=";")
			for row in csv_reader:
				_logger.info(row)
				return


				order_nr = row.get('web-order_number', False)
				if order_nr:
					order_exists = SaleOrder.search([('note', '=', order_nr)])
				if order_exists:
					update_vals = self.get_sale_order_update_vals(row)
				else:
					create_vals = self.get_sale_order_create_vals(row)


