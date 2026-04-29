from typing import Dict, Optional

import streamlit as st


_NAV_PAGES: Dict[str, object] = {}


def register_navigation_pages(nav_pages: Dict[str, object]) -> None:
    global _NAV_PAGES
    _NAV_PAGES = dict(nav_pages)


def switch_to_registered_page(page_key: str, fallback: Optional[str] = None) -> None:
    nav_pages = _NAV_PAGES or st.session_state.get("_nav_pages", {})
    target_page = nav_pages.get(page_key)

    if target_page is not None:
        st.switch_page(target_page)
        return

    if fallback is not None:
        st.switch_page(fallback)
        return

    raise RuntimeError(f"Page not registered in session navigation: {page_key}")


def switch_to_home_page() -> None:
    switch_to_registered_page("home", fallback="pages/home.py")