import logging
from odoo import http
from odoo.addons.mail.controllers.main import MailController

_logger = logging.getLogger(__name__)


class TaskMailController(MailController):

    # Handle mail view links. We do not use standard Odoo url, because we
    # show requests to authorized users only
    @http.route("/mail/view/task/<int:task>",
                type='http', auth='user', website=True)
    def mail_action_view_task(self, task, **kwargs):
        return super(
            TaskMailController, self
        ).mail_action_view(
            model='project.task', res_id=task, **kwargs)
