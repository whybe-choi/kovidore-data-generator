QUERY_FROM_SUMMARY_PROMPT = """You are an expert in creating challenging datasets for Vision Document Retrieval (VDR).
Your goal is to generate a **highly specific Korean search query** that acts as a realistic user prompt for retrieving information from a large corpus.

### 1. Document Context
You are provided with two types of summaries:

#### 1.1 Single-Section Summaries
Each `<single_section_summary>` tag contains a summary of a **specific section/page**, identified by its **actual page number** (`page`).

<single_section_summaries>
{% for summary in single_section_summary %}
<single_section_summary index="{{ loop.index0 }}">
{{ summary }}
</single_section_summary>
{% endfor %}
</single_section_summaries>

#### 1.2 Cross-Section Summary
The following is a **synthesized summary** that integrates information across all the sections above. Use this to understand the overall narrative and relationships between different sections.

<cross_section_summary>
{{ cross_section_summary }}
</cross_section_summary>

**How to use these summaries**:
* Use **single-section summaries** to identify specific facts, entities, and details located on each page.
* Use **cross-section summary** to understand how information connects across pages and to identify synthesis opportunities.
* Your query should require combining specific details from multiple sections (identified via single-section summaries) in a way that reflects the cross-section relationships (identified via cross-section summary).

### 2. Task Requirements
You must generate a structured output containing the rationale and the query itself based on the following specifications:

* **Query Type**: {{ query_type }} ({{ query_type_definition }})
* **Query Format**: {{ query_format }} ({{ query_format_definition }})

### 3. Critical Constraints for Realistic Retrieval

#### Rule 1: NO Artificial Location References
* **Strictly Forbidden**: "2페이지에서...", "다음 장에 있는...", "첫 번째 문서의...", "위에서 언급된..."
* **Reason**: The user queries the entire database and does not know the document order or page numbers.
* **Alternative**: Use **Section Headers, Table Captions, or Unique Keywords** found in the text.
    * *Bad*: "2페이지에 있는 표를 요약해."
    * *Good*: "'2024년 재무 하이라이트' 표를 요약해."

#### Rule 2: Implicit Multi-Page Synthesis
* The query must require information scattered across multiple pages, but **without explicitly stating so**.
* **Strategy**: Identify **Entity A** on one page and **Entity B** on another, then ask about their relationship.

#### Rule 3: Entity-Grounded Specificity
* Avoid generic queries like "에너지 정책을 분석해줘."
* Include specific entities found in the text: **Dates, Company Names, Regulations (e.g., ISO-27001), Project Codes, Policy Names, or Program Names**.
* However, do NOT include exact numerical values (see Rule 5).

#### Rule 4: Single Natural Query
* The query **MUST be a single unit** appropriate to its format (one question, one instruction, or one keyword cluster).
* **Strictly Forbidden Patterns**:
    * Multiple sentences: "~입니다. ~해주세요."
    * Instruction suffixes: "단, ~를 기준으로 답변하시오."
    * Explicit output format requests: "~를 근거로 제시하시오.", "~를 나열하시오."
    * Conditional clauses at the end: "단, ~를 구분하여 제공해야 합니다."
* **Examples**:
    * *Bad*: "2021년과 2022년 상승률을 비교하시오. 단, 수도권과 지방을 구분하여 제시하시오."
    * *Good*: "2021년과 2022년 수도권 및 지방의 주택 매매가격 상승률은 어떻게 달랐나요?"

#### Rule 5: Realistic Search Behavior
The query must read as if a **researcher who does NOT have the document** is searching a database by topic and keywords. This single rule covers three aspects:

**(a) No Verbatim Document Data**
* Use **conceptual references** (policy names, years, entity names) instead of **exact figures**.
* **Strictly Forbidden**: Specific monetary values, exact percentages, precise statistics copied from the document.
    * *Bad*: "에너지 요금이 €49.5/MWh에서 €94/MWh로 89% 상승한 이유는?"
    * *Good*: "2022년 프랑스 소매 에너지 요금 급등과 EDF의 ARENH 정책은 어떤 관계가 있나요?"

**(b) No Document-Aware Framing**
* **Strictly Forbidden**: "문서에서", "해당 자료의", "위 표에 따르면", "본 보고서의", "제시된 데이터를 기반으로"
* Also forbidden — **Document Title Scoping** (assumes the user already knows the document exists):
    * *Bad*: "제7차 에너지기본계획에서 원전 비중 목표는?"
    * *Good*: "2025년 일본의 원전 비중 목표"

**(c) Realistic User Knowledge**
* The user **knows**: topic area, key entities, time periods of interest.
* The user **does NOT know**: page numbers, document structure, specific numerical values, exact document titles.

### 4. Query Format Specification

#### Question Format (질문형)
* Must be a complete interrogative sentence with question endings.
* **Required elements**: Question word (무엇, 어떻게, 왜, 어떤) OR question ending (~인가요?, ~있나요?, ~했는가?)
* **Examples**:
    * "M2 광의통화 증가율이 2020년 국가채무 증가에 영향을 미쳤는가?"
    * "에너지바우처 제도의 지원 대상은 누구인가요?"

#### Instruction Format (지시형)
* Must be a command with imperative endings.
* **Required elements**: Imperative ending (~해주세요, ~하시오, ~분석하라, ~설명하라)
* **Examples**:
    * "2020년 M2 통화량과 국가채무 간의 상관관계를 분석해주세요."
    * "에너지바우처와 에너지효율개선 사업의 차이점을 비교하라."

#### Keyword Format (키워드형)
* **NO complete sentences.** Only noun phrases and search terms.
* **NO verbs, NO question words, NO sentence endings.**
* Mimics search engine input: fragmented, noun-centric.

**Keyword Format Rules**:
| Allowed | Forbidden |
|-----------|-------------|
| 명사, 명사구, 복합 명사구 | 동사 (~하다, ~이다, ~있다) |
| 관계 조사 (~의, ~와/과, ~간, ~에 따른, ~으로 인한) | 질문사 (무엇, 어떻게, 왜, 어떤) |
| 고유명사, 연도, 날짜 | 문장 종결 (~인가요, ~해주세요, ~입니까) |
| 관계 표현 (비교, 관계, 영향, 연관성, 상관관계) | 완전한 문장 구조 |
| 영문 약어 (EDF, ARENH, GDP) | 공백으로만 나열된 독립 키워드들 |
| 개념적 추상화 표현 | 문서 표 항목명·인덱스의 직접 복사 |

##### Keyword Structural Templates
A keyword query must form **one coherent noun phrase**. Every noun must be connected to its neighbors by Korean particles (의, 와/과, 간, 에 따른, 으로 인한, 내, 중, 및) that make the semantic relationship explicit.

| Template | Structure | Example |
|----------|-----------|---------|
| Comparison | A의 X와/과 B의 Y (간) 차이/비교 | "운수업의 부가가치당 에너지소비량과 수송용 에너지소비 비중 차이" |
| Correlation | A와/과 B 간 연관성/관계/상관관계 | "일반가구의 설계가중치와 도시가구의 에너지소비 간 연관성" |
| Causation | A 변화/증가/감소와 B 변화의 연관성/영향 | "부산 개별여행 비중 증가와 농수산물 구매 비중 상승의 연관성" |
| Condition | A에 따른/으로 인한 B의 변화/추이 | "스페인 용량요금 중단에 따른 전력부문 적자의 변화" |
| Composition | A 내 B와 C의 비중/분포/구성 | "EU 노동 인력 내 녹색 직업과 고도 디지털 집약 직업 간의 연령 분포" |

**Particle Removal Test**:
Strip all particles (의/와/과/간/에 따른/으로 인한/내/중/및) from the query.
* If the meaning **collapses** → Well-formed noun phrase.
* If the meaning **stays the same** → Keyword bag. Rewrite.

**Read-Aloud Test**:
Read the query aloud. If there is a natural pause splitting it into two independent chunks with no grammatical bridge → Two queries glued together. Rewrite.

**Bad → Fixed Examples**:
* "감일도서관 개관 희망도서 바로대출 지역서점 연계 독서문화 활성화 지원 사업 이동도서관 스마트도서관"
  → "감일도서관 개관 이후 희망도서 바로대출 서비스와 지역서점 연계 독서문화 사업 간의 운영 방식 차이"
* "K‑방산 폴란드 수출 비중 라틴아메리카 방위비 증가"
  → "K-방산의 폴란드 수출 비중 확대와 라틴아메리카 방위비 증가 간 연관성"
* "베트남 최종 법인세 신고 베트남 개인소득세 체계 동일 과세 기준 여부"
  → "베트남 법인세 최종 신고 체계와 개인소득세 체계의 과세 기준 동일 여부"

### 5. Quality Checklist (Self-Verification)
Before finalizing, verify ALL checks pass:

| Check | Requirement |
|-------|-------------|
| Format Compliance | Query strictly follows the specified format (question/instruction/keyword) |
| Single Unit | ONE question, ONE instruction, or ONE keyword phrase—no multiple sentences |
| No Page References | No page numbers, document indices, or positional references |
| Realistic Search | No exact values from the document, no document-aware framing, no document title scoping (Rule 5) |
| Entity-Grounded | Includes searchable entities (names, years, policy names) but not verbatim data |
| Multi-Page Implicit | Requires information from multiple pages without explicitly stating it |
| Keyword Coherence (keyword only) | **Particle Removal Test** passes: stripping particles must break the meaning |
| Single Phrase (keyword only) | **Read-Aloud Test** passes: query flows as one utterance with no independent chunks |

### 6. Output Generation
Generate the output strictly adhering to the defined JSON schema.
The query must be in **Korean** and must pass all checks in the Quality Checklist above.
**Pay special attention to the Query Format specification—the linguistic structure must match exactly.**"""