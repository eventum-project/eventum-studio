import streamlit as st
from eventum_content_manager.manage import (ContentManagementError,
                                            get_csv_sample_filenames,
                                            load_csv_sample)

from eventum_studio.components.component import BaseComponent
from eventum_studio.notifiers import NotificationLevel, default_notifier


class SampleExplorer(BaseComponent):
    """Component for displaying sample content."""

    _SHOW_PROPS = {
        'display_size': int
    }

    def _show(self) -> None:
        st.caption('Sample explorer')
        sample = st.selectbox(
            'Sample',
            options=get_csv_sample_filenames(),
            help='Select sample from repository to preview it in below table'
        )
        try:
            if sample is not None:
                sample_data = load_csv_sample(  # type: ignore[assignment]
                    path=sample
                )
            else:
                sample_data = []                # type: ignore[assignment]
        except ContentManagementError as e:
            default_notifier(
                message=f'Failed to load sample: {e}',
                level=NotificationLevel.ERROR
            )
            sample_data = []                    # type: ignore[assignment]

        total_size = len(sample_data)
        display_size = self._props['display_size']

        st.table(sample_data[:display_size])

        if total_size > display_size:
            st.text(f'and {total_size - display_size} more ...')
