"""
Backward-compatible re-export module.

The original `views.widgets.gantt_chart` used to contain both `GanttCanvas`
and `GanttChartWidget`. It has been split into:
- `views.widgets.gantt_canvas.GanttCanvas`
- `views.widgets.gantt_chart_widget.GanttChartWidget`
"""

from views.widgets.gantt_canvas import GanttCanvas  # noqa: F401
from views.widgets.gantt_chart_widget import GanttChartWidget  # noqa: F401
