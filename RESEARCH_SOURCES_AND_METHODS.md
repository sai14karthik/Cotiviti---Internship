# Research Sources and Methods

How I put together the written report and POC for the Cotiviti intern assessment.

## Question

How does healthcare content management (billing rules, coding policies, contracts, clinical guidelines) connect to what Cotiviti already does in payment accuracy?

## Research process

I spent about a week on this. Most of my time went to CMS.gov — especially the NCCI edit pages and the interoperability/prior-authorization rule summary. I also read GAO-25-107753 on fiscal year 2024 improper payments to get a sense of Medicare error scale.

For Cotiviti context I used their public Payment Accuracy page, the 2025 Everest Group press release, and a blog post on prepay/postpay integration. I did not have internal Cotiviti documents, so company details come from public sources only.

I also read Burwell (2015) on value-based payment and Sushant et al. (2024) on prior authorization workflows. Those helped me think about where manual policy review still slows teams down.

I kept a notes file with URLs and page numbers as I went. The report paraphrases sources in my own words with citations. I did not copy text from Cotiviti marketing or CMS manuals.

## Sources

**Government**
- CMS NCCI edits: https://www.cms.gov/medicare/coding-billing/national-correct-coding-initiative-ncci-edits
- CMS prior authorization / interoperability rule: https://www.cms.gov/newsroom/fact-sheets/cms-interoperability-and-prior-authorization-final-rule-cms-0057-f
- GAO improper payments FY2024: https://www.gao.gov/products/gao-25-107753
- FDA clinical decision support guidance: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software

**Cotiviti (public only)**
- Payment accuracy overview: https://www.cotiviti.com/solutions/payment-accuracy
- Everest Group leader press release (2025): https://www.cotiviti.com/press-release/cotiviti-named-highest-designated-leader-by-everest-group-in-payment-integrity-solutions-peak-matrix-assessment-2025
- Future-proofing payment integrity blog/ebook: https://blog.cotiviti.com/ebook-future-proofing-payment-integrity

**Articles**
- Burwell (2015), NEJM — value-based payment
- Sushant et al. (2024), ACL BioNLP — prior authorization workflow automation

## Citation style

APA 7th edition in the Word report bibliography.

## Proof of concept

Built in `Proof of Concept/` — Streamlit app with three tabs:

1. Summarize policy (keyword-based extractive summary)
2. Compare two sample NCCI-style versions (change table + line diff)
3. Extract PTP/MUE rules to JSON with source excerpts

Run: `streamlit run app.py` from that folder.

## Limitations

- Cotiviti savings numbers are from their own publications — I treated those as company claims, not numbers I verified independently.
- The POC uses synthetic sample text only. No real patient data or proprietary payer policies.
