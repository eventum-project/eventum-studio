from datetime import datetime

import streamlit as st
import yaml
from eventum_plugins.event.base import (EventPluginConfigurationError,
                                        EventPluginRuntimeError)
from eventum_plugins.event.jinja import (JinjaEventConfig, JinjaEventPlugin,
                                         State, SubprocessManager,
                                         SubprocessManagerMock, TemplateConfig,
                                         TemplatePickingMode)
from jinja2 import DictLoader
from pydantic import ValidationError
from streamlit_elements import editor, elements  # type: ignore[import-untyped]

from eventum_studio.components.component import BaseComponent
from eventum_studio.notifiers import NotificationLevel, default_notifier
from eventum_studio.utils.validation_prettier import prettify_errors


class TemplateRenderer(BaseComponent):
    """Component for rendering templates."""

    _SHOW_PROPS = {
        'template_content': str,
        'configuration_content': str,
    }

    def _init_state(self) -> None:
        self._session_state['rendering_result'] = ''
        self._session_state['local_vars_state'] = None
        self._session_state['shared_vars_state'] = None
        self._session_state['subprocess_manager'] = SubprocessManagerMock()

        self._session_state['mock_checkbox'] = True

    def _render(self) -> None:
        """Render currently set template content."""

        content = self._props['configuration_content']

        try:
            config_data = yaml.load(content, yaml.Loader)
        except yaml.YAMLError as e:
            default_notifier(
                message=(
                    'Failed to render template due to configuration '
                    f'parse failure: {e}'
                ),
                level=NotificationLevel.ERROR
            )
            return

        if not isinstance(config_data, dict):
            default_notifier(
                message=(
                    'Failed to render template due to invalid configuration: '
                    f'Key-value mapping expected, but got {type(config_data)}'
                ),
                level=NotificationLevel.ERROR
            )
            return

        try:
            config = JinjaEventConfig(
                mode=TemplatePickingMode.ALL,
                templates={
                    'template': TemplateConfig(     # type: ignore[call-arg]
                        template='template.jinja'
                    )
                },
                **config_data
            )
        except ValidationError as e:
            default_notifier(
                message=(
                    'Failed to render template due to invalid configuration: '
                    f'{prettify_errors(e.errors())}'
                ),
                level=NotificationLevel.ERROR
            )
            return

        timestamp = datetime.now().astimezone()
        tz = timestamp.strftime('%z')

        params = {
            'timestamp': timestamp.replace(tzinfo=None).isoformat(),
            'tz': tz
        }

        local_vars: dict | None = self._session_state['local_vars_state']
        shared_vars: State | None = self._session_state['shared_vars_state']
        subprocess_manager = self._session_state['subprocess_manager']

        try:
            plugin = JinjaEventPlugin(
                config=config,
                loader=DictLoader(
                    {'template.jinja': self._props['template_content']}
                )
            )

            if local_vars:
                _, state = local_vars.popitem()
                plugin.local_vars = {'template.jinja': state}

            if shared_vars:
                plugin.shared_vars = shared_vars

            if subprocess_manager:
                plugin.subprocess_manager = subprocess_manager

            result = plugin.render(**params)
        except (EventPluginConfigurationError, EventPluginRuntimeError) as e:
            default_notifier(
                message=(f'Failed to render template: {e}'),
                level=NotificationLevel.ERROR
            )
            return

        self._session_state['rendering_result'] = result.pop()

        self._session_state['local_vars_state'] = plugin.local_vars
        self._session_state['shared_vars_state'] = plugin.shared_vars
        self._session_state['subprocess_manager'] = plugin.subprocess_manager

        default_notifier(
            message=('Rendered successfully'),
            level=NotificationLevel.SUCCESS
        )

    def _show(self) -> None:
        st.caption(
            'Template rendering',
            help='Press render button and see the result in right side'
        )

        with elements(self._wk('template_renderer')):
            editor.MonacoDiff(
                theme='vs-dark',
                language='javascript',
                original=self._props['template_content'],
                modified=self._session_state['rendering_result'],
                options={
                    'readOnly': True,
                    'cursorSmoothCaretAnimation': True
                },
                height=560,
            )

        col1, col2 = st.columns([3, 1])
        col2.button(
            'Render',
            use_container_width=True,
            type='primary',
            on_click=self._render
        )
        col1.checkbox(
            'Mock subprocesses',
            key=self._wk('mock_checkbox'),
            on_change=(
                lambda:
                self._session_state.__setitem__(
                    'subprocess_manager',
                    SubprocessManager()
                    if not self._session_state['mock_checkbox']
                    else SubprocessManagerMock()
                )
            ),
            help='Mock performing subprocesses in template'
        )

    def clear_state(self) -> None:
        """Clear state of locals, shared and history of subprocess
        commands.
        """
        self._session_state['local_vars_state'] = None
        self._session_state['shared_vars_state'] = None
        self._session_state['subprocess_manager'] = (
            SubprocessManager()
            if not self._session_state['mock_checkbox']
            else SubprocessManagerMock()
        )

    @property
    def local_vars_state(self) -> dict:
        """Get state of template local variables."""
        locals: dict[str, State] = self._session_state['local_vars_state']

        if locals is None:
            return {}

        if locals:
            return next(iter(locals.values())).as_dict()
        else:
            return {}

    @property
    def shared_vars_state(self) -> dict:
        """Get state of template shared variables."""
        shared: State = self._session_state['shared_vars_state']

        if shared is None:
            return {}

        return shared.as_dict()

    @property
    def subprocess_commands_history(self) -> tuple[tuple[int, str], ...]:
        """Get history of commands running in templates via `subprocess`."""
        subprocess_manager = self._session_state['subprocess_manager']
        return subprocess_manager.commands_history
