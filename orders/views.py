from orders.models import OrderItem
from django.views.generic import DetailView
from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.decorators import staff_member_required


class SupplyChainHierarchyAdminView(DetailView):
    model_admin: ModelAdmin = None
    model = OrderItem
    pk_url_kwarg = 'id'
    template_name = 'admin/supply_chain_hierarchy.html'

    def __init__(
            self,
            model_admin: ModelAdmin,
            **kwargs
        ) -> None:
        super().__init__(**kwargs)
        self.model_admin = model_admin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order_item = self.object
        order_item_id = order_item.id
        context.update({
            'title': 'Supply Chain Hierarchy',
            'order_item_id': order_item_id,
            'hierarchy_data': None,
            'error': None
        })

        if order_item_id:
            try:
                hierarchy_data = self.get_supply_chain_hierarchy(order_item)
                context['hierarchy_data'] = hierarchy_data
                context['order_item'] = order_item
            except Exception as e:
                context['error'] = str(e)

        request = kwargs['request']
        context.update(
           self.get_admin_context(request=request)
        )
        return context

    def get_admin_context(self, request):
        return  self.model_admin.admin_site.each_context(request=request)

    @method_decorator(staff_member_required)
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(request=request, object=self.object)
        return self.render_to_response(context)

    def get_supply_chain_hierarchy(self, order_item):
        hierarchy = {
            'order_item': {
                'id': order_item.id,
                'name': str(order_item),
                'details': self.get_model_details(order_item)
            },
            'material_chains': []
        }

        # Get all material consumptions for this order item
        material_consumptions = order_item.material_consumptions.all()

        for consumption in material_consumptions:
            chain = self.build_material_chain(consumption)
            hierarchy['material_chains'].append(chain)

        return hierarchy

    def build_material_chain(self, consumption):
        """Build the complete chain from consumption to supplier"""
        chain = {
            'consumption': {
                'id': consumption.id,
                'details': self.get_model_details(consumption)
            }
        }

        try:
            # Restaurant Package Material
            restaurant_package_material = consumption.restaurant_package_material
            chain['restaurant_package_material'] = {
                'id': restaurant_package_material.id,
                'details': self.get_model_details(restaurant_package_material)
            }

            # Package Material
            package_material = restaurant_package_material.package_material
            chain['package_material'] = {
                'id': package_material.id,
                'details': self.get_model_details(package_material)
            }

            # Ready Material
            ready_material = package_material.ready_material
            chain['ready_material'] = {
                'id': ready_material.id,
                'details': self.get_model_details(ready_material)
            }

            # Workstation Prepared Material
            workstation_prepared_material = ready_material.workstation_prepared_material
            chain['workstation_prepared_material'] = {
                'id': workstation_prepared_material.id,
                'details': self.get_model_details(workstation_prepared_material)
            }

            # Workstation Raw Material Consumption
            workstation_raw_material_consumption = workstation_prepared_material.workstation_raw_material_consumption
            chain['workstation_raw_material_consumption'] = {
                'id': workstation_raw_material_consumption.id,
                'details': self.get_model_details(workstation_raw_material_consumption)
            }

            # Raw Material
            raw_material = workstation_raw_material_consumption.raw_material
            chain['raw_material'] = {
                'details': self.get_model_details(raw_material)
            }

            # Supplier
            supplier = raw_material.supplier
            chain['supplier'] = {
                'id': supplier.id,
                'details': self.get_model_details(supplier)
            }
        except AttributeError as e:
            chain['error'] = f"Chain broken at: {str(e)}"
        return chain

    def get_model_details(self, obj):
        return model_to_dict(obj)
