"""Policy POC for Cotiviti intern assessment — summarize, compare, extract rules."""

from __future__ import annotations

import json
from dataclasses import asdict

import pandas as pd
import streamlit as st

from engine import (
    detect_structured_changes,
    extract_mue_rules,
    extract_ptp_rules,
    line_diff,
    load_sample,
    rules_to_json,
    summarize_policy,
)

st.set_page_config(
    page_title="Policy POC",
    layout="wide",
)

st.title("Healthcare Policy POC")
st.caption("Cotiviti intern assessment · synthetic NCCI-style sample data only")

tab_summary, tab_compare, tab_rules = st.tabs(
    ["1 · Summarize Policy", "2 · Compare Versions", "3 · Extract Rules"]
)

# ── Tab 1: Summarize ─────────────────────────────────────────────────────────
with tab_summary:
    st.subheader("Summarize a billing/coding policy")
    st.write(
        "Paste policy text or load the sample file. Summaries use keyword scoring "
        "over the text — everything runs locally."
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("Load sample policy (Q1 2025)", use_container_width=True):
            st.session_state["policy_text"] = load_sample("ncci_policy_v1.txt")
    with col_b:
        uploaded = st.file_uploader("Or upload .txt", type=["txt"])

    default_text = load_sample("ncci_policy_v1.txt")
    if uploaded:
        policy_text = uploaded.read().decode("utf-8")
    else:
        policy_text = st.session_state.get("policy_text", default_text)

    policy_text = st.text_area("Policy text", value=policy_text, height=280)

    if st.button("Generate summary", type="primary"):
        result = summarize_policy(policy_text)
        st.success("Summary ready")
        meta = result["metadata"]
        if meta:
            st.write(
                f"**Version:** {meta.get('version', 'n/a')} · "
                f"**Effective:** {meta.get('effective_date', 'n/a')}"
            )
        c1, c2, c3 = st.columns(3)
        c1.metric("PTP edits found", result["stats"]["ptp_edits"])
        c2.metric("MUE rules found", result["stats"]["mue_rules"])
        c3.metric("Document size", f"{result['stats']['characters']:,} chars")
        st.markdown("**Key points**")
        for bullet in result["bullets"]:
            st.markdown(f"- {bullet}")
        st.caption(f"Method: {result['method']}")

# ── Tab 2: Compare ─────────────────────────────────────────────────────────────
with tab_compare:
    st.subheader("Compare two policy versions")
    st.write(
        "Shows what changed between Q1 and Q2 sample releases — the kind of diff a "
        "Cotiviti analyst would need before updating prepay edit tables."
    )

    v1 = load_sample("ncci_policy_v1.txt")
    v2 = load_sample("ncci_policy_v2.txt")

    left, right = st.columns(2)
    with left:
        st.markdown("**Previous (Q1 2025)**")
        st.text_area("v1", value=v1, height=200, label_visibility="collapsed")
    with right:
        st.markdown("**Updated (Q2 2025)**")
        st.text_area("v2", value=v2, height=200, label_visibility="collapsed")

    if st.button("Run comparison", type="primary"):
        changes = detect_structured_changes(v1, v2)
        st.markdown("### Detected changes")
        if not changes:
            st.info("No structured changes detected.")
        else:
            rows = [
                {
                    "Type": c.change_type,
                    "Detail": c.detail,
                    "Before": c.old_value or "—",
                    "After": c.new_value or "—",
                }
                for c in changes
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        with st.expander("Full line-by-line diff (unified)"):
            st.code(line_diff(v1, v2), language="diff")

# ── Tab 3: Extract rules ───────────────────────────────────────────────────────
with tab_rules:
    st.subheader("Extract machine-readable rules")
    st.write(
        "Parses PTP code pairs and MUE unit limits into JSON that could feed a "
        "claims-editing engine after human review."
    )

    source = st.radio(
        "Source document",
        ["Q1 2025 sample", "Q2 2025 sample", "Custom text"],
        horizontal=True,
    )
    if source == "Q1 2025 sample":
        rule_text = load_sample("ncci_policy_v1.txt")
    elif source == "Q2 2025 sample":
        rule_text = load_sample("ncci_policy_v2.txt")
    else:
        rule_text = st.text_area("Custom policy", height=200)

    if st.button("Extract rules", type="primary"):
        ptp = extract_ptp_rules(rule_text)
        mue = extract_mue_rules(rule_text)

        st.markdown(f"**Found {len(ptp)} PTP edits and {len(mue)} MUE rules**")

        st.markdown("#### PTP edits")
        st.dataframe(
            pd.DataFrame([asdict(r) for r in ptp]),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("#### MUE limits")
        st.dataframe(
            pd.DataFrame([asdict(r) for r in mue]),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("#### JSON export (draft rules for engine load)")
        st.code(rules_to_json(rule_text), language="json")

        st.download_button(
            "Download rules.json",
            data=rules_to_json(rule_text),
            file_name="extracted_rules.json",
            mime="application/json",
        )

st.divider()
st.caption(
    "Workflow: load policy → summarize → diff when a new version drops → export rules with citations."
)
