from ckan.lib.base import BaseController, render
from ckanext.evaluator.controllers.evaluator import EvaluatorController

evalController = EvaluatorController()


class ViewController(BaseController):
    def organization_evaluation_view(self, id):
        ''' Render dataset evaluation view with the evaluation data

        dataset_evaluation_view(id) -> render the view

        render the view of evaluation result
        '''

        extra_vars = evalController.organization_evaluation(id)
        return render('organization/evaluation.html', extra_vars=extra_vars)

    def dataset_evaluation_view(self, id):
        ''' Render dataset evaluation view with the evaluation data

        dataset_evaluation_view(id) -> render the view

        render the view of evaluation result
        '''
        extra_vars = evalController.dataset_evaluation(id)
        return render('package/evaluation.html', extra_vars=extra_vars)
