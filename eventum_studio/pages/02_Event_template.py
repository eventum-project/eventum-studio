import os

import streamlit as st

from eventum_studio.components.component import persist_state
from eventum_studio.components.template_configuration_editor import \
    TemplateConfigurationEditor
from eventum_studio.components.template_editor import TemplateEditor
from eventum_studio.components.template_manager import TemplateManager
from eventum_studio.components.template_renderer import TemplateRenderer
from eventum_studio.components.template_state_viewer import TemplateStateViewer
from eventum_studio.theme import apply_theme

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ICON_PATH = os.path.join(BASE_DIR, '../static/favicon.ico')

persist_state()
st.set_page_config(
    page_title='Eventum Studio',
    page_icon=ICON_PATH,
    layout='wide',
    initial_sidebar_state='expanded'
)
apply_theme()

for key in ['template_content', 'config_content']:
    if key not in st.session_state:
        if key == 'config_content':
            st.session_state[key] = (
                'params: { }\n'
                'samples: { }\n'
            )
        else:
            st.session_state[key] = ''

manager = TemplateManager(
    props={
        'get_content_callback': lambda: st.session_state['template_content'],
        'set_content_callback': (
            lambda content:
            st.session_state.__setitem__('template_content', content)
        )
    }
)
editor = TemplateEditor(
    props={
        'content': st.session_state['template_content'],
        'read_only': manager.is_empty,
        'on_change': (
            lambda value:
            st.session_state.__setitem__('template_content', value)
        )
    }
)
config_editor = TemplateConfigurationEditor(
    props={
        'content': st.session_state['config_content'],
        'on_change': (
            lambda value:
            st.session_state.__setitem__('config_content', value)
        )
    }
)
renderer = TemplateRenderer(
    props={
        'template_content': st.session_state['template_content'],
        'configuration_content': st.session_state['config_content']
    }
)
state_viewer = TemplateStateViewer(
    props={
        'local_vars': renderer.local_vars_state,
        'shared_vars': renderer.shared_vars_state,
        'subprocess_commands_history': renderer.subprocess_commands_history,
        'clear_state_callback': renderer.clear_state
    }
)

with st.sidebar:
    manager.show()

editor_tab, configuration_tab, rendering_tab, state_tab = st.tabs(
    ['Template', 'Configuration', 'Rendering', 'State']
)

with editor_tab:
    editor.show()

with configuration_tab:
    config_editor.show()

with rendering_tab:
    renderer.show()

with state_tab:
    state_viewer.show()
