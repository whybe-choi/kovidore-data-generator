# 📘 Dataset Generation Pipeline

This document describes how KoViDoRe and Ko-VDR-Train-Public were created.

KoViDoRe is a benchmark dataset for Korean Visual Document Retrieval, built from real Korean public documents. Ko-VDR-Train-Public is a synthetic training dataset for the same task, released as a page-level query-page supervision set. Each final row pairs a synthetic Korean retrieval query with a relevant document page image and its parsed text.

<p align="center">
  <img src="https://raw.githubusercontent.com/whybe-choi/kovidore-data-generator/main/assets/cover.png" alt="Overall Dataset Generation Pipeline" width="820" />
</p>

## 🔍 Key Characteristics

- Built from real Korean public PDF documents
- Preserves both page images and parsed page text
- Combines context-based and summary-based synthetic query generation
- Keeps only query-page pairs whose relevance mapping is consistent between the generation stage and the filtering stage

## 🛠 Creation Workflow

The public dataset was created through six major stages:

1. Document collection
2. Page-level corpus construction
3. Summary generation
4. Synthetic query generation
5. Relevance mapping and dataset assembly
6. Public-release filtering

## 1️⃣ Document Collection

The process began with a curated set of Korean PDF documents from government agencies, public institutions, and public-interest organizations.

The source set was selected to reflect realistic visual document retrieval conditions rather than simple text lookup. Documents were chosen because they often contain:

- long-form narrative content
- tables and charts
- policy or procedural language
- structured layouts
- information spread across multiple pages

This makes the resulting dataset more useful for systems that must interpret both the visual and textual structure of public documents.

## 2️⃣ Page-Level Corpus Construction

Each PDF was converted into a structured page-level corpus.

For every page, the corpus construction stage produced:

- a rendered page image
- extracted markdown text
- serialized layout elements
- the original page number within the document

This stage created the retrieval corpus that later query generation and relevance mapping were built on top of.

**Command:**
```bash
python build_corpus.py --subsets {subset}
```

**Output:** `data/{subset}/corpus/data.parquet`

<p align="center">
  <img src="https://raw.githubusercontent.com/whybe-choi/kovidore-data-generator/main/assets/pipeline/0_convert_image_to_markdown.png" alt="Page-Level Corpus Construction" width="720" />
</p>

## 3️⃣ Summary Generation

Before queries were generated, the pipeline created intermediate summaries to expose document structure and cross-page relationships more clearly.

Two forms of summaries were used:

- Single-section summaries
- Cross-section summaries

Single-section summaries describe individual sections. Cross-section summaries are created by combining multiple single-section summaries from the same document and synthesizing their content.

These summaries help surface relationships that may not be obvious from a single page alone, which is especially important for multi-page retrieval supervision.

**Command:**
```bash
bash scripts/run.sh --subsets {subset} --task single_section_summary
```

**Output:** `data/{subset}/single_section_summary/`

<p align="center">
  <img src="https://raw.githubusercontent.com/whybe-choi/kovidore-data-generator/main/assets/pipeline/1_1_single_section_summary.png" alt="Single-Section Summary Generation" width="720" />
</p>

**Command:**
```bash
bash scripts/run.sh --subsets {subset} --task cross_section_summary
```

**Output:** `data/{subset}/cross_section_summary/`

<p align="center">
  <img src="https://raw.githubusercontent.com/whybe-choi/kovidore-data-generator/main/assets/pipeline/1_2_cross_section_summary.png" alt="Cross-Section Summary Generation" width="720" />
</p>

## 4️⃣ Synthetic Query Generation

Queries were generated through two complementary routes.

Upstage Solar Pro 3 was used for synthetic query generation in both routes.

### A. Context-Based Query Generation

In the context-based route, the generator used local page windows directly. This route tends to produce queries grounded in nearby page context and local multi-page continuity.

**Command:**
```bash
bash scripts/run.sh --subsets {subset} --task query_from_context
```

**Output:** `data/{subset}/query_from_context/`

<p align="center">
  <img src="https://raw.githubusercontent.com/whybe-choi/kovidore-data-generator/main/assets/pipeline/2_1_query_from_context.png" alt="Context-Based Query Generation" width="720" />
</p>

### B. Summary-Based Query Generation

In the summary-based route, the generator used cross-section summaries instead of raw page windows. This route tends to produce broader document-level retrieval prompts, including:

- cross-section comparisons
- document-level synthesis queries
- multi-section retrieval prompts

**Command:**
```bash
bash scripts/run.sh --subsets {subset} --task query_from_summary
```

**Output:** `data/{subset}/query_from_summary/`

<p align="center">
  <img src="https://raw.githubusercontent.com/whybe-choi/kovidore-data-generator/main/assets/pipeline/2_2_query_from_summary.png" alt="Summary-Based Query Generation" width="720" />
</p>

### Query Diversity

The query generator was designed to diversify both intent and surface form.

The dataset includes multiple query types, such as:

- compare-contrast
- open-ended
- enumerative
- multi-hop
- extractive
- numerical
- boolean

It also includes multiple query formats, such as:

- question
- instruction
- keyword

This design was intended to better reflect realistic retrieval behavior over complex document collections.

## 5️⃣ Relevance Mapping

> [!Note]
> For the KoViDoRe benchmark, relevance mapping results were manually verified by human annotator to ensure the reliability of the evaluation set. For Ko-VDR-Train-Public, this human verification step was not applied; the relevance mapping relied solely on the automated two-stage process described below.

During query generation, the pipeline also performed an initial, implicit form of relevance mapping by identifying which input pages were actually relevant to the generated query. This step was used to determine which pages provided supporting evidence, since not all pages included in the generation input were necessarily relevant to the final query.

After query generation, a separate filtering stage performed a second, explicit relevance mapping step to judge page-level relevance again. Only queries whose relevance mapping was consistent across both stages were retained for the final dataset.

This two-stage process was important because synthetic query generation alone does not guarantee a clean alignment between a query and its supporting pages. A single query may depend on multiple pages, and some pages may contain only partial but still necessary evidence.

As a result, the dataset was organized as query-page pairs rather than one row per query, since a single query can be associated with multiple relevant pages.

**Command:**
```bash
bash scripts/run.sh --subsets {subset} --task filter_query_from_context
bash scripts/run.sh --subsets {subset} --task filter_query_from_summary
```

**Output:** `data/{subset}/filter_query_from_context/` or `data/{subset}/filter_query_from_summary/`

<p align="center">
  <img src="https://raw.githubusercontent.com/whybe-choi/kovidore-data-generator/main/assets/pipeline/3_relevance_mapping.png" alt="Relevance Mapping" width="720" />
</p>

## 6️⃣ Low-Quality Query Filtering

Before public release, additional filtering was applied to remove low-quality queries from the broader internal generation output.

Upstage Solar Pro 3 was also used during the filtering workflow to support query quality review.

This cleanup was based on rule-based filtering and focused on excluding query patterns that did not meet the desired release standard. In particular, queries were removed when they:

- contained a specific person's name
- were composed of two separate sentences rather than a single natural query
- included overly detailed information that was unlikely to reflect realistic retrieval behavior
- simply listed entities or terms without forming a coherent query

As a result, the public dataset is a cleaner training-oriented subset of the original generation output.

## 📂 What the Final Rows Represent

Each released row corresponds to one aligned query-page pair containing:

- a synthetic Korean retrieval query
- a source document identifier
- a relevant page image
- parsed text and layout information for that page

This makes the dataset suitable for training and evaluating visual document retrieval systems that operate over page screenshots, OCR-like text, and structured page content together.

---

## 🗂 Directory Structure

After running the full pipeline, the data directory for each subset follows this layout:

```
data/{subset}/
├── pdfs/                                    # Place input PDF files here
├── images/                                  # Generated page images from PDFs
├── corpus/
│   └── data.parquet                         # Parsed corpus data
├── seed/                                    # Preprocessed seed files for each task
│   ├── seed_for_single_section_summary.parquet
│   ├── seed_for_cross_section_summary.parquet
│   ├── seed_for_query_from_context.parquet
│   ├── seed_for_query_from_summary.parquet
│   ├── seed_for_filter_query_from_context.parquet
│   └── seed_for_filter_query_from_summary.parquet
├── single_section_summary/                  # Pipeline output
├── cross_section_summary/                   # Pipeline output
├── query_from_context/                      # Pipeline output
├── query_from_summary/                      # Pipeline output
├── filter_query_from_context/               # Pipeline output
└── filter_query_from_summary/               # Pipeline output
```

> **Note:** Before running the pipeline, place your PDF files in `data/{subset}/pdfs/`.

---

## ▶️ Running the Pipeline

The full pipeline runs in five steps. Replace `{subset}` with your target subset (e.g., `hr`, `energy`, `economic`, `cybersecurity`).

```bash
# Step 1: Build corpus from PDF documents
python build_corpus.py --subsets {subset}

# Step 2: Generate single-section summaries
bash scripts/run.sh --subsets {subset} --task single_section_summary

# Step 3: Generate cross-section summaries
bash scripts/run.sh --subsets {subset} --task cross_section_summary

# Step 4: Generate queries (choose one or both routes)
bash scripts/run.sh --subsets {subset} --task query_from_context
bash scripts/run.sh --subsets {subset} --task query_from_summary

# Step 5: Relevance mapping
bash scripts/run.sh --subsets {subset} --task filter_query_from_context
bash scripts/run.sh --subsets {subset} --task filter_query_from_summary
```

To use a specific model, pass the `--model_alias` flag:

```bash
bash scripts/run.sh --subsets {subset} --task {task} --model_alias upstage-solar-pro3
```

---

## ⚙️ Customizing Model Providers

Model providers and configurations are defined in [src/kovidore_data_generator/config.py](src/kovidore_data_generator/config.py).

### Adding a New Provider

```python
from data_designer.essentials import ModelProvider, ModelConfig, ChatCompletionInferenceParams

custom_provider = ModelProvider(
    name="custom",
    endpoint="https://api.custom-provider.com/v1",
    api_key="CUSTOM_API_KEY",  # Environment variable name
)

model_providers = [upstage_provider, openai_provider, custom_provider]
```

### Adding a New Model Configuration

```python
model_configs = [
    # ... existing configs ...
    ModelConfig(
        alias="custom-model",       # Use this alias with --model_alias flag
        model="model-name",         # Actual model name from the provider
        provider="custom",          # Must match provider name above
        inference_parameters=ChatCompletionInferenceParams(
            max_tokens=4096,
            temperature=0.7,
            top_p=0.9,
        ),
    ),
]
```

The currently available model aliases are:

| Alias | Model | Provider |
|-------|-------|----------|
| `upstage-solar-pro2` | solar-pro2-251215 | Upstage |
| `upstage-solar-pro3` | solar-pro3-260323 | Upstage |
| `openai-gpt-5-mini` | gpt-5-mini | OpenAI |
