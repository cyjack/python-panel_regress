from linearmodels import PanelOLS
from linearmodels.panel import generate_panel_data
panel_data = generate_panel_data()
mod = PanelOLS.from_formula('y ~ 1 + x1 + EntityEffects', panel_data.data)
res = mod.fit(cov_type='clustered', cluster_entity=True)
print(res)

from linearmodels import PanelOLS
mod = PanelOLS(y, x, entity_effects=True)
res = mod.fit(cov_type='clustered', cluster_entity=True)