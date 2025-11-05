"""Initialize insights_agent package"""
from .visualizer import (
    generate_revenue_plot,
    generate_segment_overview,
    render_campaign_console,
    render_segment_modal,
    merge_segments_extra_fields,
    segment_chart_interactions,
    render_kpi_widgets,
)
from .segment_customers import load_customer_data, segment_customers
from .summarize_insights import generate_insight_summary

__all__ = [
    "generate_revenue_plot",
    "generate_segment_overview",
    "render_campaign_console",
    "render_segment_modal",
    "merge_segments_extra_fields",
    "segment_chart_interactions",
    "render_kpi_widgets",
    "load_customer_data",
    "segment_customers",
    "generate_insight_summary",
]