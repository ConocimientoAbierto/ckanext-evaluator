import routes.mapper
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class EvaluatorPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('fanstatic', 'evaluator')

    def before_map(self, route_map):
        with routes.mapper.SubMapper(route_map,
            controller='ckanext.evaluator.controllers.view:ViewController') as m:
            m.connect('organization_evaluation', '/organization/evaluation/{id}', action='organization_evaluation_view', ckan_icon='bar-chart')

            m.connect('dataset_evaluation', '/dataset/evaluation/{id}', action='dataset_evaluation_view', ckan_icon='bar-chart')

        return route_map

    def after_map(self, route_map):
        return route_map

    def get_helpers(self):
        ''' Register the get_total_points_organization function in EvaluatorController as a helper function.
        '''
        from ckanext.evaluator import helpers as evaluator_helpers

        return {
                'evaluator_total_points_organization': evaluator_helpers.total_points_organization
                }
