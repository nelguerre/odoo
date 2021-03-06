# -*- coding: utf-8 -*-

import werkzeug
from openerp import http
from openerp.http import request

from openerp.tools.translate import _

class Rating(http.Controller):

    @http.route('/rating/<string:token>/<int:rate>', type='http', auth="public")
    def open_rating(self, token, rate, **kwargs):
        assert rate in (1, 5, 10), "Incorrect rating"
        rating = request.env['rating.rating'].sudo().search([('access_token', '=', token)])
        if not rating:
            return request.not_found()
        rate_names={
            5: _("not satisfied"),
            1: _("highly dissatisfied"),
            10: _("satisfied")
        }
        rating.sudo().write({'rating': rate, 'consumed': True})
        return request.render('rating.rating_external_page_submit', {
            'rating': rating, 'token': token,
            'rate_name': rate_names[rate], 'rate': rate
        })
        return request.not_found()

    @http.route(['/rating/<string:token>/<int:rate>/submit_feedback'], type="http", auth="public", method=['post'])
    def submit_rating(self, token, rate, **kwargs):
        rating = request.env['rating.rating'].sudo().search([('access_token', '=', token)])
        if not rating:
            return request.not_found()
        record_sudo = request.env[rating.res_model].sudo().browse(rating.res_id)
        record_sudo.rating_apply(rate, token=token, feedback=kwargs.get('feedback'))
        # redirect to the form view if logged person
        if request.session.uid:
            return werkzeug.utils.redirect('/web#model=%s&id=%s&view_type=form' % (record_sudo._name, record_sudo.id))
        return request.render('rating.rating_external_page_view')
