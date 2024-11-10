from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_studio_how_can_we_make_your_dreams_come_true = fields.Text(string="How can we make your dreams come true?")
    x_studio_text_field_ctg1R = fields.Text(string="")
    x_studio_membership_code = fields.Text(string="Membership Code")
    x_studio_education_contact = fields.Char(string="Education - Contact")
    x_studio_shopify_code_1 = fields.Char(string="Shopify Code")
    x_studio_dob_contact = fields.Date(string="DoB - Contact")
    x_studio_referrer = fields.Many2one('res.partner',string="Referrer", domain=[('partner_id.membership_type','=','central')])
    x_studio_stage2 = fields.Char(string="Stage2")
    x_studio_mobile_contact = fields.Char(string="mobile - contact",related='partner_id.mobile')
    x_studio_allow_access_to_app_1 = fields.Boolean(string="Allow Access to App",related="partner_id.x_studio_allow_access_to_app")
    x_studio_many2many_field_TjqQy = fields.Many2many('crm.tag','x_crm_lead_crm_tag_rel',string="What do you currently do for exercise?")
    x_studio_name_of_university = fields.Char(string="Name of University/Institution")
    x_studio_referral_to_be_interviewed = fields.Boolean(string="Referral to be interviewed")
    x_studio_referral_accepted = fields.Boolean(string="Referral Accepted")
    x_studio_send_membership_code = fields.Boolean(string="Send Membership Code")
    x_studio_hap_owner = fields.Boolean(string="HAP Owner")
    x_studio_do_you_currently_workout_or_exercise = fields.Boolean(string="Do you currently workout or exercise")
    x_studio_what_do_you_currently_do_for_exercise = fields.Boolean(string="Do you currently workout or exercise")
    x_studio_are_you_currently_a_member_in_any_sports_club = fields.Boolean(string="Are you currently a member in any sports club?")
    x_studio_do_you_currently_workout_or_exercise_1 = fields.Boolean(string="Do you currently workout or exercise")
    x_studio_referral_accepted_date = fields.Date(string="Referral accepted Date")
    x_studio_downpayment_done_date = fields.Date(string="Downpayment Done Date")
    x_studio_occupation_company_name_contact = fields.Char(string="Occupation &amp; Company name - Contact")
    x_studio_national_id__2 = fields.Char(string="National ID #")
    x_studio_mobile_city = fields.Char(string="mobile - city")
    x_studio_what_services_that_you_would_like_to_see_at_the_club = fields.Char(invisible=True)
    x_studio_highest_level_of_education_received_by_spouse = fields.Selection(selection=[('University Degree', 'University Degree'), ('Masters Degree', 'Masters Degree'), ('PHD', 'PHD'), ('High School Diploma', 'High School Diploma'), ('N/A', 'N/A')], string="Highest Level of Education Received by Spouse")
    x_studio_how_often_do_you_eat_at_the_club = fields.Selection(selection=[('Sometimes', 'Sometimes'), ('Everytime you go', 'Everytime I go'), ('Not at all', 'Not at all')], string="How often do you eat at the club?")
    x_studio_are_you_currently_a_member_in_any_sports_club_1 = fields.Selection(selection=[('Yes', 'Yes'), ('No', 'No')], string="Are you currently a member in any sports club?")
    x_studio_relationship_to_referrer_1 = fields.Selection(selection=[('A Friend', 'A Friend'), ('A First Degree Relative (parent/sibling/first cousin)', 'A First Degree Relative (parent/sibling/first cousin)'), ('A Second Degree Relative (second cousin/any other relative)', 'A Second Degree Relative (second cousin/any other relative)')], string="Relationship to Referrer")
    x_studio_relationship_to_referrer = fields.Selection(selection=[('A Friend', 'A Friend'), ('A First Degree Relative (parent/sibling/first cousin)', 'A First Degree Relative (parent/sibling/first cousin)'), ('A Second Degree Relative (second cousin/any other relative)', 'A Second Degree Relative (second cousin/any other relative)')], string="Relationship to Referrer")
    x_studio_how_often_do_you_go_to_your_preferred_club_1 = fields.Selection(selection=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('more than 5', 'more than 5')], string="How often do you go to your preferred club?")

    x_studio_how_often_do_you_go_to_your_preferred_club = fields.Selection(selection=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('more than 5', 'more than 5')], string="How often do you go to your preferred club?", invisible=True)

    x_studio_how_did_you_hear_about_us = fields.Selection(selection=[('Friends &amp; family (currently KODE members)', 'Friends &amp; family (currently KODE members)'), ('Friends &amp; Family (non-KODE members)', 'Friends &amp; Family (non-KODE members)'), ('Social Media pages', 'Social Media pages'), ('Online communication streams (KODE website, press releases, online features etc.)', 'Online communication streams (KODE website, press releases, online features etc.)'), ('Seeing or hearing about KODE offline activities (KODE initial invitation kit, KODE branded items with members etc.)', 'Seeing or hearing about KODE offline activities (KODE initial invitation kit, KODE branded items with members etc.)')], string="How did you hear about us?")
    x_studio_hap_owner_2 = fields.Selection(selection=[('Yes', 'Yes'), ('No', 'No')], string="HAP Owner?")
    x_studio_email_to_send = fields.Selection(selection=[('Referral Rejected', 'Referral Rejected'), ('Option to share new referral name/number', 'has not been identified as an existing KODE member'), ('we were unable to reach your referral', 'we were unable to reach your referral'), ('we were unable to receive a confirmed referral', 'we were unable to receive a confirmed referral')], string="Email to send")
    x_studio_area_of_home_address = fields.Selection(selection=[('New Cairo', 'New Cairo'), ('Sherouk', 'Sherouk'), ('HeliopolisNasr City', 'Heliopolis'), ('Nasr City', 'Nasr City'), ('Maadi', 'Maadi'), ('Mohandeseen', 'Mohandeseen'), ('Zamalek', 'Zamalek'), ('6th of October', '6th of October'), ('Garden City', 'Garden City'), ('Other', 'Other')],string="Area of Home Address")
    x_studio_rejection_reason_2 = fields.Char(string="Rejection Reason 2")
    x_studio_rejection_reason_3 = fields.Char(string="Rejection Reason 3")
    x_studio_membership_id = fields.Char(string="Referrer Membership ID")
    x_studio_name_of_sports_club = fields.Char(string="Name of Sports Club")
    x_studio_what_school_nursery_does_your_child_attend = fields.Char(string="What school/ Nursery does your child attend?")
    x_studio_besides_sports_what_are_your_interests_and_hobbies_1 = fields.Char(string="Besides sports, what are your interests and hobbies?")

    x_studio_besides_sports_what_are_your_interests_and_hobbies = fields.Char(invisible=True)
    x_studio_company_name = fields.Char(string="Spouse's Company Name")
    x_studio_referrer_name = fields.Char(string="Referrer Name")
    x_studio_national_id_ = fields.Char(string="National ID #")
    x_studio_rejection_reason_1 = fields.Char(string="Rejection Reason 1")
    x_studio_phone_number_of_referrer = fields.Char(string="Phone Number of Referrer")
    x_studio_char_field_npScq = fields.Char(string="Name of Institution where your spouse received their highest degree")
    x_studio_occupation = fields.Char(string="Spouse's Occupation")
    x_studio_name_of_spouse = fields.Char(string="Name of Spouse")

    def write(self, vals):
        res = super().write(vals)
        if vals.get('type') and vals['type'] == 'opportunity':
            self.partner_id.x_studio_referrer = self.x_studio_referrer
        elif vals.get('x_studio_referrer') and self.type == 'opportunity':
            self.partner_id.x_studio_referrer = vals['x_studio_referrer']
        return res

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_studio_date_of_birth = fields.Date(string="Date of Birth")
    x_studio_importing_reference = fields.Integer(string="Importing/Exporting Reference")
    x_studio_referrer = fields.Many2one('res.partner',string="Referrer", domain=[('membership_type','=','central')])
    x_studio_central_member_name = fields.Many2one('res.partner',string="Central Member Name")
    x_studio_referred_members = fields.One2many('res.partner','x_studio_referrer',string="Referred Members")
    x_studio_associated_family_members = fields.One2many('res.partner','x_studio_central_member_name',string="Referred Members")
    x_studio_education = fields.Char(string="Education")
    x_studio_allow_access_to_app = fields.Boolean(string="Allow Access to App")
    x_studio_separated_from = fields.Many2one('res.partner', string="Separated From")
    x_studio_many2one_field_fXQ4J = fields.Many2one('res.partner', string="X Studio Many2One Field Fxq4J")
    x_studio_separated_member = fields.Boolean(string="Separated Member?")
    x_studio_hap_customer = fields.Boolean(string="HAP Customer?")
    x_studio_central_member = fields.Boolean(string="Central Member")
    x_studio_occupation_company_name = fields.Char(string="Occupation &amp; Company Name")
    x_studio_idpassport_number = fields.Char(string="ID/Passport Number")
    x_studio_gender = fields.Selection(selection=[('Male', 'Male'), ('Female', 'Female')], string="Gender")
    x_studio_member_type = fields.Selection(selection=[('Central Member', 'Central Member'), ('Family Member', 'Family Member')],string="Member Type")
    x_studio_relationship_to_central_member = fields.Selection(selection=[('Spouse', 'Spouse'), ('Parent', 'Parent'), ('Child', 'Child'), ('Sibling', 'Sibling'), ('Step-child', 'Step-child'), ('Ex-spouse', 'Ex-spouse')], string="Relationship to Central Member")
    x_studio_stage_3 = fields.Char(string="Stage")
    x_studio_stage_2 = fields.Char(string="Stage")
    x_studio_university = fields.Char(string="University")
    x_studio_hap_customer_code = fields.Char(string="HAP Customer Code")


class AccountMove(models.Model):
    _inherit = 'account.move'
    x_studio_description = fields.Text(string="Description")


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    x_studio_related_batch_cheque = fields.Many2one('x_batch_cheques', string="Related Batch (Cheque)")
    x_studio_3_cheque = fields.Integer(string='Number of batch cheques')
    x_studio_paymob_order_no = fields.Integer(string="Paymob Order No.")
    x_studio_collected_amount = fields.Monetary(string="Collected Amount")
    x_studio_batch_cheque = fields.Many2one('x_batch_cheques', string="Batch Cheque")
    x_studio_batch_cheque_amount = fields.Selection(selection=[('3-Cheque Batch', '3-Cheque Batch'), ('6-Cheque Batch', '6-Cheque Batch'), ('12-Cheque Batch', '12-Cheque Batch')], string="Batch Cheque Amount")
    x_studio_batch_cheque_date = fields.Date(string="Batch Cheque Date")
    x_studio_first_cheque_is_today = fields.Boolean(string="First Cheque is Today")
    x_studio_collected = fields.Boolean(string="Is collected")
    x_studio_is_parent = fields.Boolean(string="Is Added")
    x_studio_bouncedreturned = fields.Boolean(string="Bounced/Returned")
    x_studio_batch_cheque_date_1 = fields.Date(string="Batch cheque date")
    x_studio_cheque_bounced_date = fields.Date(string="Cheque Bounced Date")
    x_studio_due_date = fields.Date(string="Cheque Due Date")
    x_studio_date_of_collection = fields.Date(string="Date of Collection")
    x_studio_location = fields.Selection(selection=[('In Company', 'In Company'), ('In Bank', 'In Bank')],string="Location")
    x_studio_payment_method = fields.Selection(selection=[('cash', 'Cash'), ('Cash in Bank', 'Cash in Bank'), ('visa', 'Visa'), ('paymob', 'Paymob'), ('cheque', 'Cheque')], string="Payment Method")
    x_studio_bo = fields.Selection(selection=[('Bounced/returned', 'Bounced/returned')],string="Bo")
    x_studio_cheque_number = fields.Char(string="Cheque Number")
    x_studio_batch_cheque_ref = fields.Char(string="Batch cheque ref")
    x_studio_description = fields.Char(string="Description")


class x_batch_cheques(models.Model):
    _name = 'x_batch_cheques'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    x_active = fields.Boolean(string="Active")
    x_name = fields.Char(string="Name")
    x_studio_partner_id = fields.Many2one('res.partner', string="Contact")
    x_currency_id = fields.Many2one('res.currency',string="Currency")
    x_studio_partner_email = fields.Char(string="Email")
    x_studio_cheques = fields.One2many('account.payment','x_studio_related_batch_cheque', string="Central Member Name")
    x_studio_cheque_cashed_today = fields.Boolean(string='Cheque Cashed Today')
    x_studio_date_of_cheque_receipt = fields.Date(string="Date of Cheque Receipt")
    x_studio_first_cheque_due_date = fields.Date(string="First Cheque Due Date")
    x_studio_todays_date = fields.Date(string="Today's date")
    x_studio_second_cheque_date = fields.Date(string="Second Cheque Date")
    x_studio_cheque_3 = fields.Integer(string="Cheque 3")
    x_studio_number_of_months_between_cheques = fields.Integer(string="Number of Months Between Cheques")
    x_studio_amount = fields.Monetary(string="Amount")
    x_studio_description = fields.Text(string="Description")
    x_studio_next_number = fields.Integer(string="CANCELLED")
    x_studio_next_number_1 = fields.Integer(string="Cheque Reference")
    x_studio_cheque_reference = fields.Char(string="Cancelled")
    x_studio_amount_of_cheques_to_create = fields.Selection(selection=[('3', '3'), ('6', '6'), ('12', '12')], string="Amount of Cheques to Create")
    x_studio_notes = fields.Text(string="Notes")
    x_studio_partner_phone = fields.Char(string="Phone")
    x_studio_selection_field_UG6bP = fields.Selection(selection=[('new', 'New'), ('running', 'Running (on time)'), ('pending', 'Bounced/Returned')],string="Pipeline status bar")
    x_studio_user_id = fields.Many2one('res.users', string="Responsible")
    x_studio_sequence = fields.Integer(string="Sequence")
    x_studio_many2one_field_FDjEY = fields.Many2one('ir.sequence',string="Sequence")
    x_studio_membership_code = fields.Text(string="Membership Code")
    x_studio_sale_orders = fields.One2many('sale.order','partner_id',related='x_studio_partner_id.sale_order_ids')


class SurveyQuestionLine(models.Model):
    _inherit = "survey.user_input.line"

    x_studio_related_field_r7Y2q = fields.Char(string="New Related Field")
    x_studio_partner = fields.Many2one('res.partner',string="Partner")
    x_studio_related_field_LhCnv = fields.Many2one('res.partner',string="New Related Field")


class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    x_studio_record_question_id = fields.Integer(string="Record Question ID")
    x_studio_triggering_question_id = fields.Integer(string="Triggering Question ID")








