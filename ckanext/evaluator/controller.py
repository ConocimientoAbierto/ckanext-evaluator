from ckan.lib.base import render, c, abort
from ckan.controllers.group import GroupController
from ckan import model, logic
import ckan.plugins as plugins
# import ckan.plugins.toolkit.c as c

# class EvaluatorController(base.BaseController):
class EvaluatorController(GroupController):

    def evaluation(self, id):

        try:
            ## Get data from DB
            self.group_type = 'organization'
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author,
                       'schema': self._db_to_form_schema(group_type=self.group_type),
                       'for_view': True, 'extras_as_string': True}
            data_dict = {'id': id}

            c.group_dict = self._action('organization_show')(context, data_dict)
            c.group = context['group']
        except logic.NotFound:
            # abort(404, _('Resource not found'))
            abort(404, 'Esto es un 404 desde mi controller')
        except logic.NotAuthorized:
            abort(401, 'Esto es un 401 desde mi controller')

        return render('organization/evaluation.html')


    def dataset_evaluation(self, id):

        try:
            ## Get data from DB
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author,
                       'for_view': True, 'extras_as_string': True,
                       'auth_user_obj': c.userobj}
            data_dict = {'id': id}

            c.pkg_dict = logic.get_action('package_show')(context, data_dict)
            c.pkg = context['package']
        except logic.NotFound:
            # abort(404, _('Resource not found'))
            abort(404, 'Esto es un 404 desde mi controller')
        except logic.NotAuthorized:
            abort(401, 'Esto es un 401 desde mi controller')

        return render('dataset/evaluation.html')
