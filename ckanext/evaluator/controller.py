import ckan.lib.base as base
import ckan.logic as logic
# import ckan.plugins as p
import ckan.plugins.toolkit as toolkit

class EvaluatorController(base.BaseController):

    def evaluation(self, id):
        ## TODO esto debería funcionar pero no parece que no llega al controladador

        try:
            toolkit.c.group_dict = toolkit.get_action('organization_show')(
                None, {'id': id}
            )
        except logic.NotFound:
            base.abort(404, _('Resource not found'))
        except logic.NotAuthorized:
            base.abort(401, _('Unauthorized to edit this resource'))

        return base.render('organization/evaluation.html')
