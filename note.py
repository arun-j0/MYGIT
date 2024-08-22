from bokeh.plotting import figure
from bokeh.models import FreehandDrawTool

import streamlit as st


p = figure(x_range=(0, 10), y_range=(0, 10), width=400, height=400)

renderer = p.multi_line([[1, 1]], [[1, 1]], line_width=1, alpha=0.4, color='red')

draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=99999)
p.add_tools(draw_tool)
p.toolbar.active_drag = draw_tool

st.bokeh_chart(p)