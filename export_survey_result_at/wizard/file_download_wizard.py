# -*- coding: utf-8 -*-

from odoo import models, fields


class FileDownloadWizard(models.TransientModel):
    _name = 'file.download.wizard'
    _description = 'File Download Wizard'

    file = fields.Binary(string="File", required=True)
    filename = fields.Char('File Name', required=True)
