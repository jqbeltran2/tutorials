from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"

    _sql_constraints = [
        ("check_price", "CHECK(price > 0)", "The price must be strictly positive"),
    ]

    _order = "price desc"

    price = fields.Float("Price", required=True)
    state = fields.Selection(selection=[('pending', 'Pending'), ('accepted', 'Accepted'), ('refused', 'Refused')],
                            required=True,
                            copy=False,
                            default="pending")
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)

    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.date_deadline = date + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity = (offer.date_deadline - date).days
    
    def action_accept(self):
        for record in self:
            if record.state == "accepted":
                raise UserError("An offer as already been accepted.")
            record.state = "accepted"
            record.property_id.state = "offer_accepted"
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id.id

    def action_refuse(self):
        for record in self:
            record.state = "refused"

    @api.model_create_multi
    def create(self, values):
        properties = {}
        for value in values:
            property_id = value['property_id']
            if property_id not in properties:
                properties[property_id] = []
            properties[property_id].append(value)

        for property_id, offers in properties.items():
            if self.env['estate.property'].browse(property_id).state == 'sold':
                raise UserError(("You cannot create an offer for a sold property."))

            best_price = self.env['estate.property'].browse(property_id).best_price
            records = super().create(offers)

            for record in records:
                if float_compare(record.price, best_price, 2) == -1:
                    raise UserError(("The price of your offer should not be lower than the best offer."))

                record.property_id.state = 'offer_received'

        return records