# -*- coding: utf-8 -*-

import base64
import io
import logging

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class ExportSurveyResultWizard(models.TransientModel):
    _name = 'export.survey.result.wizard'
    _description = 'Export Survey Result Wizard'

    only_completed_surveys = fields.Boolean('Only Completed Surveys', default=False)
    convert_answers_into_points = fields.Boolean('Convert answers into points', default=False)
    survey_id = fields.Many2one('survey.survey', 'Survey')

    @api.model
    def default_get(self, fields):
        res = super(ExportSurveyResultWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id', False)
        if self.env.context.get('active_model') == 'survey.survey' and active_id:
            if 'survey_id' in fields:
                res['survey_id'] = active_id
        return res

    def export_survey_answers(self):
        # Create a workbook and add a worksheet.
        fp = io.BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})
        worksheet.write(0, 0, 'Person', bold)
        index = 1
        answer_column_index = {}
        for question in self.survey_id.question_and_page_ids.filtered(lambda x: not x.is_page):
            if question.question_type == 'multiple_choice':
                for suggested_answer in question.suggested_answer_ids:
                    worksheet.write(0, index, question.title, bold)
                    worksheet.write(1, index, suggested_answer.value, bold)
                    answer_column_index.setdefault('{}-{}'.format(question.id, suggested_answer.id), index)
                    index += 1
            elif question.question_type == 'matrix':
                for matrix_row in question.matrix_row_ids:
                    worksheet.write(0, index, question.title, bold)
                    worksheet.write(1, index, matrix_row.value, bold)
                    answer_column_index.setdefault('{}-{}'.format(question.id, matrix_row.id), index)
                    index += 1
            else:
                worksheet.write(0, index, question.title, bold)
                answer_column_index.setdefault('{}-{}'.format(question.id, ''), index)
                index += 1

        domain = [('survey_id', '=', self.survey_id.id)]
        if self.only_completed_surveys:
            domain.extend([('state', '=', 'done')])

        answers = self.env['survey.user_input'].search(domain)
        row = 2
        for answer in answers:
            worksheet.write(row, 0, answer.partner_id and answer.partner_id.name or '')
            for user_input_line in answer.user_input_line_ids:
                if user_input_line.skipped:
                    continue

                is_scoring = self.convert_answers_into_points
                if user_input_line.question_id.question_type == 'text_box':
                    answer_index = answer_column_index.get('{}-{}'.format(user_input_line.question_id.id, ''))
                    if answer_index or answer_index == 0:
                        worksheet.write(row, answer_index, user_input_line.value_text_box)
                elif user_input_line.question_id.question_type == 'char_box':
                    answer_index = answer_column_index.get('{}-{}'.format(user_input_line.question_id.id, ''))
                    if answer_index or answer_index == 0:
                        worksheet.write(row, answer_index, user_input_line.value_char_box)
                elif user_input_line.question_id.question_type == 'numerical_box':
                    answer_index = answer_column_index.get('{}-{}'.format(user_input_line.question_id.id, ''))
                    if answer_index or answer_index == 0:
                        worksheet.write(row, answer_index,
                                        user_input_line.answer_score if is_scoring and user_input_line.answer_score != 0 else user_input_line.value_numerical_box)
                elif user_input_line.question_id.question_type == 'date':
                    answer_index = answer_column_index.get('{}-{}'.format(user_input_line.question_id.id, ''))
                    if answer_index or answer_index == 0:
                        worksheet.write(row, answer_index,
                                        user_input_line.answer_score if is_scoring and user_input_line.answer_score != 0 else user_input_line.value_date.strftime(
                                            DEFAULT_SERVER_DATE_FORMAT))
                elif user_input_line.question_id.question_type == 'datetime':
                    answer_index = answer_column_index.get('{}-{}'.format(user_input_line.question_id.id, ''))
                    if answer_index or answer_index == 0:
                        worksheet.write(row, answer_index,
                                        user_input_line.answer_score if is_scoring and user_input_line.answer_score != 0 else user_input_line.value_datetime.strftime(
                                            DEFAULT_SERVER_DATETIME_FORMAT))
                elif user_input_line.question_id.question_type == 'simple_choice':
                    answer_index = answer_column_index.get('{}-{}'.format(user_input_line.question_id.id, ''))
                    if answer_index or answer_index == 0:
                        worksheet.write(row, answer_index,
                                        user_input_line.answer_score if is_scoring and user_input_line.answer_score != 0 else user_input_line.suggested_answer_id.value)
                elif user_input_line.question_id.question_type == 'multiple_choice':
                    answer_index = answer_column_index.get(
                        '{}-{}'.format(user_input_line.question_id.id, user_input_line.suggested_answer_id.id))
                    if answer_index or answer_index == 0:
                        worksheet.write(row, answer_index,
                                        user_input_line.answer_score if is_scoring else user_input_line.suggested_answer_id.value)
                elif user_input_line.question_id.question_type == 'matrix':
                    answer_index = answer_column_index.get(
                        '{}-{}'.format(user_input_line.question_id.id, user_input_line.matrix_row_id.id))
                    if answer_index or answer_index == 0:
                        worksheet.write(row, answer_index, user_input_line.suggested_answer_id.value)
            row += 1

        workbook.close()
        fp.seek(0)
        data = fp.read()

        wizard_id = self.env['file.download.wizard'].create({
            'file': base64.encodebytes(data),
            'filename': '%s - Survey Answers.xlsx' % self.survey_id.title
        })
        action = self.env.ref('export_survey_result_at.file_download_wizard_action').sudo().read()[0]
        action.update({
            'target': 'new',
            'res_id': wizard_id.id
        })
        return action
