# starting-ragchatbot-codebase-main

---
the chat interface displays query responses with source citations. I need to modify it so each source becomes a clickable link that opens the corresponding lesson video in a new tab:
1. when courses are processed into chunks in @backend/document_processor.py, the link of each lesson is stored in the course_catelog collection.
2. modify _format results in @backend/search_tools.py, so that the lesson links are also returned.
3. the links should be embedded invisibly（no visible URL text）

---
Add a 'NEW CHAT' button to the left sidebar above the courses section.
When clicked, it should:
- clear the current conversation in the chat window
- start a new session without page reload
- handle proper cleanup on both @frontend and @backend
- match the styling of existing sections (Courses, Try asking) - same font size, color and uppercase formatting

---
Using the playwright MCP server visit 127.0.0.1:8000 and view the new chat button. I want that button to look the same as the other links below for Courses and Try Asking. Make sure this is left aligned and that the border is removed

---
In @backend/search_tools.py, add a second tool alongside the existing content-related tool. this new tool should handle course outline queries.
- functionality
    - input: Course title
    - output: Course title, course link, and complete lesson list
    - for each lesson: lesson number, lesson title
- data source: Course metadata collection of the vector store
- update the system prompt in @backend/ai_generator so that the course title, course link, the number and title of each lesson are all returned to address an outline-related queries.
- make sure that the new tool is registerd in the system.

>  The system now supports two distinct query types:
>  - Content queries: "What does lesson 5 cover?" → Uses search_course_content
>  - Outline queries: "What is the outline of the MCP course?" → Uses get_course_outline

---
I need you to:

1. Write tests to evaluate the outputs of the execute method of the CourseSearchTool in @backend/search_tools.py
2. Write tests to evaluate if @backend/ai_generator.py correctly calls for the CourseSearchTool
3. Write tests to evaluate how the RAG system is handling the content-query related questions.

Save the tests in a tests folder within @backend. Run those tests against the current system to identify which components are failing. Propose fixes based on what the tests reveal is broken.


---
The @EDA.ipynd contains exploratory data analysis on e-commerce data in @ecommerce_data, focusing on sales metrics for 2023. Keep the same analysis and graphs, and improve the structure and documentation of the notebook.

Review the existing notebook and identify:
- what bussiness metrics are currently calculated
- what visualizations are created
- what data transformations are performed
- any code quality issues or inefficiencies

**refactoring requirments**
1. notebook structure & documentation
    - add proper documentation and markdown cells with clear header and a brief explanation for the section
    - organize into logical sections:
        - introduction & business objectives
        - data loading & configuration
        - data preparation & transformation
        - business metrics calculation (revenue, product, geographic, customer experience analysis)
        - summary of observations
    - add table of contents at the beginning
    - include data dictionary explaining key columns and business terms
2. code quality improvements
    - create reusable functions with docstrings
    - implement consistent naming and formatting
    - create separate Python files:
        - business_metrics.py, containing business metric calculations only
        - data_loader.py loading, processing and cleaning the data
3. enhanced visualizations
    - improve all plots with:
        - clear and descriptive titles
        - proper axis labels with units
        - legends where needed
        - appropriate chart types for the data
        - include date range in plot titles or captions
        - use consistent color business-oriented color schemes
4. configurable analysis framework
    the notebook shows the computation of metrics for a specific date range(entire year of 2023 compared to 2022).
    refactor the code so that the data is first filtered according to configurable month and year & implement general-purpose metric calculations.

**deliverables expected**
- refactored Jupyter notebook(EDA_refactored.ipynb) with all improvement
- business metrics module(business_metrics.py) with documented functions
- requirements file(requirements.txt) listing all dependencies
- README section explaining how to use the refactored analysis