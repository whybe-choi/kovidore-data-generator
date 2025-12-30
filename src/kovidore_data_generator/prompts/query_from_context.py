QUERY_FROM_CONTEXT_PROMPT = """You are an expert in creating challenging datasets for Vision Document Retrieval (VDR).
Your goal is to generate a **highly specific Korean search query** that acts as a realistic user prompt for retrieving information from a large corpus.

### 1. Document Context
The following XML-like tags contain the markdown text extracted from a sequence of document pages.
The `<document index="...">` tags are for your internal reasoning ONLY. **Do NOT mention these indices in the final query.**

<documents>
{% for doc in markdown %}
<document index="{{ loop.index0 }}">
{{ doc }}
</document>
{% endfor %}
</documents>

### 2. Task Requirements
You must generate a structured output containing the rationale and the query itself based on the following specifications:

* **Query Type**: {{ query_type }} ({{ query_type_definition }})
* **Query Format**: {{ query_format }} ({{ query_format_definition }})

### 3. Critical Constraints for Realistic Retrieval
To ensure the query works in a real search engine where the user does not know the page numbers:

#### Rule 1: NO Artificial Location References
* **Strictly Forbidden**: "2페이지에서...", "다음 장에 있는...", "첫 번째 문서의...", "위에서 언급된..."
* **Reason**: The user queries the entire database and does not know the document order or page numbers.
* **Alternative**: Use **Section Headers, Table Captions, or Unique Keywords** found in the text.
    * ❌ *Bad*: "2페이지에 있는 표를 요약해."
    * ✅ *Good*: "'2024년 재무 하이라이트' 표를 요약해." (Assuming '2024년 재무 하이라이트' is the actual text in the document)

#### Rule 2: Implicit Multi-Page Synthesis
* The query must require information that happens to be scattered across multiple pages, but without explicitly stating "look at multiple pages".
* **Strategy**:
    * Identify **Entity A** on Page 1 (e.g., a definition or policy name).
    * Identify **Entity B** on Page 2 or 3 (e.g., a specific data point or implementation detail).
    * Create a query that asks for the relationship between **Entity A** and **Entity B**.
    * *Example*: "Why did the **[Project A from Page 1]** fail to meet the targets set in the **[Q3 Report Table from Page 2]**?"

#### Rule 3: Entity-Grounded Specificity
* Avoid generic queries like "에너지 정책을 분석해줘."
* Include specific entities found in the text: **Dates, Company Names, Regulations (e.g., ISO-27001), Project Codes, Policy Names, or Program Names**.
* However, do NOT include exact numerical values (see Rule 5).

### 4. Query Quality Constraints

#### Rule 4: Single Natural Query
* The query **MUST be a single unit** appropriate to its format (one question, one instruction, or one keyword cluster).
* **Strictly Forbidden Patterns**:
    * Multiple sentences: "~입니다. ~해주세요."
    * Instruction suffixes: "단, ~를 기준으로 답변하시오."
    * Explicit output format requests: "~를 근거로 제시하시오.", "~를 나열하시오."
    * Conditional clauses at the end: "단, ~를 구분하여 제공해야 합니다."
* **Examples**:
    * ❌ *Bad*: "A와 B는 차이가 있습니다. 구체적으로 비교해주세요."
    * ❌ *Bad*: "2021년과 2022년 상승률을 비교하시오. 단, 수도권과 지방을 구분하여 제시하시오."
    * ✅ *Good*: "A 정책과 B 제도의 지원 대상 및 방식은 어떻게 다른가요?"
    * ✅ *Good*: "2021년과 2022년 수도권 및 지방의 주택 매매가격 상승률은 어떻게 달랐나요?"

#### Rule 5: No Verbatim Document Data in Query
* The user does **NOT** know the exact numbers, percentages, or specific values in the document before searching.
* Use **conceptual references** (policy names, years, entity names) instead of **exact figures**.
* **Strictly Forbidden**: Specific monetary values, exact percentages, precise statistics copied from the document.
* **Examples**:
    * ❌ *Bad*: "에너지 요금이 €49.5/MWh에서 €94/MWh로 89% 상승한 이유는?"
    * ❌ *Bad*: "34,477.4 tCO2 감축량 중 34,433.3 tCO2를 차지하는 사업은?"
    * ✅ *Good*: "2022년 프랑스 소매 에너지 요금 급등과 EDF의 ARENH 정책은 어떤 관계가 있나요?"
    * ✅ *Good*: "'에너지 신산업' 전략에서 가장 큰 CO2 감축 기여를 하는 세부사업은 무엇인가요?"

#### Rule 6: No Document-Aware Framing
* The query must sound like the user is **searching for information in a database**, NOT **querying a known document they already have**.
* The user does **NOT** know that a specific document exists before searching.

**Type A - Direct Document References (Strictly Forbidden)**:
* "문서에서", "해당 자료의", "위 표에 따르면", "본 보고서의"
* "분석된 ~의 개수", "제시된 데이터를 기반으로"
* "~항목의 수치를 근거로", "표에 나타난"

**Type B - Document Title Scoping (Strictly Forbidden)**:
* Using a specific document title to scope the query: "~보고서에서", "~계획에서", "~법에서", "~백서에서"
* This assumes the user already knows the document exists.
* **Examples**:
    * ❌ *Bad*: "2019년 2분기 사이버 위협 동향 보고서에서 Clop 랜섬웨어를 다룬 장은?"
    * ❌ *Bad*: "제7차 에너지기본계획에서 원전 비중 목표는?"
    * ❌ *Bad*: "GX2040 비전에서 제시된 탄소중립 전략은?"
    * ✅ *Good*: "2019년 2분기 Clop 랜섬웨어 공격 사례와 5G 보안 인식도 조사 결과"
    * ✅ *Good*: "일본 2025년 에너지기본계획 원전 비중 목표"
    * ✅ *Good*: "일본 GX2040 탄소중립 전략 주요 내용"

**Reasoning**: In a real VDR scenario, users search by **topic and keywords**, not by document titles they already know. The retrieval system should find the relevant document, not the user.

#### Rule 7: Realistic User Intent
* Imagine a **researcher or analyst** querying a large document database. They know:
    * Topic area (e.g., energy policy, economic indicators, cybersecurity)
    * Key entities (e.g., EDF, ARENH, M2 광의통화, 에너지바우처)
    * Time periods of interest (e.g., 2020년, 2022년)
* They do **NOT** know:
    * Exact page numbers or document structure
    * Specific numerical values before retrieval
    * Which tables or sections contain the answer
    * The exact title of the document that contains the information
* The query should reflect **genuine information-seeking behavior**.

### 5. Query Format Specification

The query format determines the linguistic structure of your output. **Follow the specified format strictly.**

#### Question Format (질문형)
* Must be a complete interrogative sentence with question endings.
* **Required elements**: Question word (무엇, 어떻게, 왜, 어떤) OR question ending (~인가요?, ~있나요?, ~했는가?)
* **Examples**:
    * "M2 광의통화 증가율이 2020년 국가채무 증가에 영향을 미쳤는가?"
    * "에너지바우처 제도의 지원 대상은 누구인가요?"
    * "2022년 EDF 적자의 주요 원인은 무엇인가요?"

#### Instruction Format (지시형)
* Must be a command with imperative endings.
* **Required elements**: Imperative ending (~해주세요, ~하시오, ~분석하라, ~설명하라)
* **Examples**:
    * "2020년 M2 통화량과 국가채무 간의 상관관계를 분석해주세요."
    * "에너지바우처와 에너지효율개선 사업의 차이점을 비교하라."
    * "미국과 일본의 2025년 에너지 정책을 요약해주세요."

#### Keyword Format (키워드형)
* **NO complete sentences.** Only noun phrases and search terms.
* **NO verbs, NO question words, NO sentence endings.**
* Mimics search engine input: fragmented, noun-centric.
* Use spaces to separate concept clusters.
* **Examples**:
    * "M2 광의통화 증가율 2020년 국가채무 영향"
    * "에너지바우처 vs 에너지효율개선 지원대상 차이"
    * "EDF ARENH 고정가격 2022년 적자 원인"
    * "미국 일본 중국 2025년 에너지 정책 행정명령"
    * "프랑스 소매전력요금 상승 에너지요금 TURPE 세금"
    * "랜섬웨어 공격 사례 2024년 2월 3월"

**Keyword Format Rules**:
| ✅ Allowed | ❌ Forbidden |
|-----------|-------------|
| 명사, 명사구 | 동사 (~하다, ~이다, ~있다) |
| 고유명사, 연도, 날짜 | 질문사 (무엇, 어떻게, 왜, 어떤) |
| "vs", 비교 키워드 | 문장 종결 (~인가요, ~해주세요, ~입니까) |
| 공백으로 구분된 키워드 | 완전한 문장 구조 |
| 영문 약어 (EDF, ARENH, GDP) | 조사 남용 (~은/는, ~이/가, ~을/를) |

### 6. Quality Checklist (Self-Verification)
Before finalizing the query, verify that it passes ALL of the following checks:

| Check | Requirement |
|-------|-------------|
| ✅ Format Compliance | Query strictly follows the specified format (question/instruction/keyword) |
| ✅ Single Unit | Query is ONE question, ONE instruction, or ONE keyword cluster—no multiple sentences |
| ✅ No Page References | No mention of page numbers, document indices, or positional references |
| ✅ No Exact Values | No specific numbers, percentages, or monetary values copied from the document |
| ✅ No Document Framing | Does not assume the user already has the document ("문서에서", "~보고서에서") |
| ✅ No Document Title Scoping | Does not use document titles to scope the query |
| ✅ Entity-Grounded | Includes searchable entities (names, years, policy names) but not verbatim data |
| ✅ Multi-Page Implicit | Requires information from multiple pages without explicitly stating it |
| ✅ Realistic Intent | Sounds like a genuine search query someone would type |

### 7. Good vs Bad Examples by Format

#### Question Format
| Quality | Example | Reason |
|---------|---------|--------|
| ✅ Good | "M2 광의통화 증가율이 2020년 국가채무 증가에 영향을 미쳤는가?" | Single question, entity-grounded, no exact values |
| ❌ Bad | "A와 B는 차이가 있습니다. 어떻게 다른가요?" | Multiple sentences |
| ❌ Bad | "€49.5에서 €94로 상승한 이유는 무엇인가요?" | Contains exact document values |
| ❌ Bad | "제7차 에너지기본계획에서 원전 목표는 무엇인가요?" | Document title scoping |

#### Instruction Format
| Quality | Example | Reason |
|---------|---------|--------|
| ✅ Good | "에너지바우처와 에너지효율개선 사업의 지원 방식을 비교하라." | Single instruction, clear entities |
| ❌ Bad | "비교하시오. 단, 지원대상을 구분하여 제시하시오." | Instruction suffix with conditions |
| ❌ Bad | "문서에서 제시된 데이터를 분석해주세요." | Document-aware framing |

#### Keyword Format
| Quality | Example | Reason |
|---------|---------|--------|
| ✅ Good | "미국 일본 중국 2025년 에너지 정책 행정명령" | Noun phrases only, no verbs |
| ✅ Good | "Clop 랜섬웨어 2019년 2분기 공격 사례 5G 보안" | Topic keywords without document title |
| ❌ Bad | "2025년에 발표된 미국, 일본, 중국의 에너지 정책은 어떤 것이 있나요?" | Complete sentence (should be keyword) |
| ❌ Bad | "에너지 정책 분석하다 비교하다" | Contains verbs |
| ❌ Bad | "사이버 위협 동향 보고서에서 랜섬웨어" | Document title scoping |

### 8. Output Generation
Generate the output strictly adhering to the defined JSON schema.
The query must be in **Korean** and must pass all checks in the Quality Checklist above.
**Pay special attention to the Query Format specification—the linguistic structure must match exactly.**"""
